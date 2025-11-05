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
    
    # Step 3: Scrape comments
    print("\n[3/5] Scraping comments...")
    print("-" * 60)
    comments_file = scrape_comments(media_ids_file, os.path.join(output_dir, f"{username}_comments.json"))
    if not comments_file:
        print("⚠️ Failed to scrape comments. Continuing...")
    else:
        print(f"✅ Comments saved to: {comments_file}\n")
    
    # Step 4: Scrape likes
    print("\n[4/5] Scraping likes...")
    print("-" * 60)
    likes_file = scrape_likes(media_ids_file, os.path.join(output_dir, f"{username}_likers.txt"))
    if not likes_file:
        print("⚠️ Failed to scrape likes. Continuing...")
    else:
        print(f"✅ Likes saved to: {likes_file}\n")
    
    # Step 5: Scrape followers
    print("\n[5/5] Scraping followers...")
    print("-" * 60)
    followers_file = scrape_followers(username)
    if not followers_file:
        print("⚠️ Failed to scrape followers. Continuing...")
    else:
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
        print(f"✅ Followers saved to: {followers_file}\n")

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

    # Enrich leads by invoking leads_data.py (expects usernames.txt -> output.json)
    leads_data_out = os.path.join(output_dir, f"{username}_leads_data.json")
    temp_usernames = os.path.join(os.getcwd(), "usernames.txt")
    temp_output = os.path.join(os.getcwd(), "output.json")
    try:
        shutil.copyfile(leads_file, temp_usernames)
        subprocess.run([sys.executable, os.path.join(os.getcwd(), "leads_data.py")], check=False)
        if os.path.exists(temp_output):
            shutil.move(temp_output, leads_data_out)
            print(f"✅ Leads data saved to: {leads_data_out}\n")
        else:
            print("⚠️ leads_data.py did not produce output.json")
    except Exception as e:
        print(f"⚠️ Failed to run leads_data.py: {e}")
    finally:
        # Cleanup temp files if present
        try:
            if os.path.exists(temp_usernames):
                os.remove(temp_usernames)
        except Exception:
            pass
    
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

