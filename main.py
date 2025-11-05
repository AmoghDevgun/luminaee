#!/usr/bin/env python3
"""
Main script to orchestrate all Instagram scrapers.
Takes a username as input and runs all scrapers in sequence.
"""

import sys
import os
import json
import shutil
import time
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from profile import scrape_profile
from getMediaId import scrape_media_ids
from comments import scrape_comments
from likes import scrape_likes
from followers import scrape_followers
import subprocess

def main():
    """Main function to run all scrapers"""
    # Get username input
    username = input("Enter Instagram username: ").strip()
    
    if not username:
        print("❌ Please enter a valid username.")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Starting scraping process for @{username}")
    print(f"{'='*60}\n")
    
    # Ensure output directory
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Scrape profile posts
    print("\n[1/5] Scraping profile posts...")
    print("-" * 60)
    postid_file = scrape_profile(username)
    if not postid_file:
        print("❌ Failed to scrape profile posts. Exiting.")
        sys.exit(1)
    postid_out = os.path.join(output_dir, f"{username}_postid.txt")
    try:
        shutil.move(postid_file, postid_out)
    except Exception:
        # If it's already in place or move fails, fall back to copy
        try:
            shutil.copyfile(postid_file, postid_out)
        except Exception:
            pass
    print(f"✅ Profile posts saved to: {postid_out}\n")
    
    # Step 2: Get media IDs
    print("\n[2/5] Extracting media IDs...")
    print("-" * 60)
    media_ids_file = scrape_media_ids(postid_out, os.path.join(output_dir, f"{username}_media_ids.txt"))
    if not media_ids_file:
        print("❌ Failed to extract media IDs. Exiting.")
        sys.exit(1)
    print(f"✅ Media IDs saved to: {media_ids_file}\n")
    
    # Steps 3-5: Run comments, likes, followers in parallel
    print("\n[3-5] Running comments, likes, and followers in parallel...")
    print("-" * 60)
    comments_target = os.path.join(output_dir, f"{username}_comments.json")
    likes_target = os.path.join(output_dir, f"{username}_likers.txt")

    comments_file = None
    likes_file = None
    followers_file = None

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(scrape_comments, media_ids_file, comments_target): "comments",
            executor.submit(scrape_likes, media_ids_file, likes_target): "likes",
            executor.submit(scrape_followers, username): "followers",
        }
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
                if task == "comments":
                    comments_file = result
                    if comments_file:
                        print(f"✅ Comments saved to: {comments_file}")
                    else:
                        print("⚠️ Failed to scrape comments.")
                elif task == "likes":
                    likes_file = result
                    if likes_file:
                        print(f"✅ Likes saved to: {likes_file}")
                    else:
                        print("⚠️ Failed to scrape likes.")
                elif task == "followers":
                    followers_file = result
                    if followers_file:
                        followers_out = os.path.join(output_dir, f"{username}_followers.txt")
                        try:
                            shutil.move(followers_file, followers_out)
                            followers_file = followers_out
                        except Exception:
                            try:
                                shutil.copyfile(followers_file, followers_out)
                                followers_file = followers_out
                            except Exception:
                                pass
                        print(f"✅ Followers saved to: {followers_file}")
                    else:
                        print("⚠️ Failed to scrape followers.")
            except Exception as e:
                print(f"⚠️ {task} task failed: {e}")
    print()

    # Aggregate leads (usernames) from followers, likers, comments
    print("\n[6/6] Aggregating leads...")
    leads = set()
    try:
        if likes_file and os.path.exists(likes_file):
            with open(likes_file, "r", encoding="utf-8") as f:
                for line in f:
                    uname = line.strip()
                    if uname:
                        leads.add(uname)
    except Exception:
        pass

    try:
        if followers_file and os.path.exists(followers_file):
            with open(followers_file, "r", encoding="utf-8") as f:
                for line in f:
                    uname = line.strip()
                    if uname:
                        leads.add(uname)
    except Exception:
        pass

    try:
        if comments_file and os.path.exists(comments_file):
            with open(comments_file, "r", encoding="utf-8") as f:
                comments = json.load(f)
                for c in comments:
                    uname = (c or {}).get("username")
                    if uname:
                        leads.add(uname)
    except Exception:
        pass

    leads_file = os.path.join(output_dir, f"{username}_leads.txt")
    with open(leads_file, "w", encoding="utf-8") as f:
        for uname in sorted(leads):
            f.write(uname + "\n")
    print(f"✅ Leads saved to: {leads_file}")

    # Enrich leads by invoking multiple leads_data.py subprocesses in parallel
    leads_data_out = os.path.join(output_dir, f"{username}_leads_data.json")
    try:
        with open(leads_file, "r", encoding="utf-8") as f:
            all_leads = [line.strip() for line in f if line.strip()]
    except Exception:
        all_leads = []

    if all_leads:
        # Chunk leads and run parallel workers based on CPU and lead volume
        def chunks(seq, n):
            for i in range(0, len(seq), n):
                yield seq[i:i+n]

        worker_outputs = []

        def run_worker(batch):
            with tempfile.TemporaryDirectory() as tmpdir:
                ufile = os.path.join(tmpdir, "usernames.txt")
                ofile = os.path.join(tmpdir, "output.json")
                with open(ufile, "w", encoding="utf-8") as uf:
                    uf.write("\n".join(batch))
                subprocess.run([sys.executable, os.path.join(os.getcwd(), "leads_data.py")], cwd=tmpdir, check=False)
                if os.path.exists(ofile):
                    try:
                        with open(ofile, "r", encoding="utf-8") as jf:
                            return json.load(jf)
                    except Exception:
                        return []
                return []

        cpu = os.cpu_count() or 4
        max_workers = min(16, max(4, cpu * 2))
        # Aim for ~2-3 batches per worker to keep them busy
        target_batches = max_workers * 3
        batch_size = max(10, (len(all_leads) + target_batches - 1) // target_batches)

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(run_worker, batch) for batch in chunks(all_leads, batch_size)]
            for fut in as_completed(futures):
                try:
                    worker_outputs.extend(fut.result() or [])
                except Exception:
                    pass

        try:
            with open(leads_data_out, "w", encoding="utf-8") as f:
                json.dump(worker_outputs, f, ensure_ascii=False, indent=2)
            print(f"✅ Leads data saved to: {leads_data_out}\n")
        except Exception as e:
            print(f"⚠️ Failed writing leads data: {e}")
    else:
        print("⚠️ No leads to enrich.")

    # Rank leads for the niche
    try:
        if os.path.exists(leads_data_out):
            with open(leads_data_out, "r", encoding="utf-8") as f:
                enriched_data = json.load(f)
        else:
            enriched_data = []

        # Clean and dedupe
        seen = set()
        cleaned = []
        for item in enriched_data or []:
            uname = (item.get("username") or "").strip().lower()
            if not uname or uname in seen:
                continue
            seen.add(uname)
            cleaned.append({
                "username": uname,
                "full_name": (item.get("full_name") or "").strip(),
                "followers": int(item.get("follower_count") or 0),
                "following": int(item.get("following_count") or 0),
                "bio": (item.get("biography") or "").strip().lower(),
            })

        if cleaned:
            # Signals and scoring per updated rules
            keywords = ["fitness", "gym", "training", "health", "workout"]
            for row in cleaned:
                # Lowercase everything per cleaning rule
                row["full_name"] = (row["full_name"] or "").lower()
                bio = row["bio"]
                # Bio relevance count and tiered score
                matches = sum(1 for kw in keywords if kw in bio)
                if matches >= 2:
                    bio_score = 1.0
                elif matches == 1:
                    bio_score = 0.6
                else:
                    bio_score = 0.0

                # Authenticity: real name has >1 words
                authenticity = 1 if len((row["full_name"] or "").strip().split()) > 1 else 0

                # Follow ratio balance (best near 1)
                followers = max(0, int(row["followers"]))
                following = max(0, int(row["following"]))
                if followers > 0 and following > 0:
                    ratio = following / followers
                    # Score 1 at ratio==1, declines towards 0 as deviates
                    follow_score = min(ratio, 1/ratio)
                    if follow_score > 1:
                        follow_score = 1.0
                    if follow_score < 0:
                        follow_score = 0.0
                else:
                    follow_score = 0.0

                # Weighted total: 70% bio, 20% authenticity, 10% ratio
                lead_score = 0.7 * bio_score + 0.2 * authenticity + 0.1 * follow_score
                # Ensure within [0,1]
                if lead_score < 0:
                    lead_score = 0.0
                if lead_score > 1:
                    lead_score = 1.0

                # Classification; enforce niche mention requirement for Medium/High
                if lead_score > 0.7 and bio_score > 0:
                    category = "High potential"
                elif lead_score >= 0.4 and bio_score > 0:
                    category = "Medium potential"
                else:
                    category = "Low potential"

                row["lead_score"] = round(lead_score, 4)
                row["category"] = category

            # Sort descending by score
            ranked = sorted(cleaned, key=lambda x: x["lead_score"], reverse=True)

            ranked_json = os.path.join(output_dir, f"{username}_leads_ranked.json")
            ranked_csv = os.path.join(output_dir, f"{username}_leads_ranked.csv")

            with open(ranked_json, "w", encoding="utf-8") as f:
                json.dump([
                    {
                        "username": r["username"],
                        "full_name": r["full_name"],
                        "followers": r["followers"],
                        "following": r["following"],
                        "bio": r["bio"],
                        "lead_score": round(r["lead_score"], 4),
                        "category": r["category"],
                    }
                    for r in ranked
                ], f, ensure_ascii=False, indent=2)

            with open(ranked_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["username", "full_name", "followers", "following", "bio", "lead_score", "category"])
                for r in ranked:
                    writer.writerow([
                        r["username"],
                        r["full_name"],
                        r["followers"],
                        r["following"],
                        r["bio"],
                        f"{r['lead_score']:.4f}",
                        r["category"],
                    ])

            print(f"✅ Ranked leads saved to: {ranked_json} and {ranked_csv}")
        else:
            print("⚠️ No enriched leads to rank.")
    except Exception as e:
        print(f"⚠️ Ranking failed: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("✅ Scraping process completed!")
    print(f"{'='*60}")
    print("\nGenerated files:")
    print(f"  - {postid_out}")
    if media_ids_file:
        print(f"  - {media_ids_file}")
    if comments_file:
        print(f"  - {comments_file}")
    if likes_file:
        print(f"  - {likes_file}")
    if followers_file:
        print(f"  - {followers_file}")
    print(f"  - {leads_file}")
    print(f"  - {leads_data_out}")
    print()

if __name__ == "__main__":
    main()

