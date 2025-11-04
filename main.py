#!/usr/bin/env python3
"""
Main script to orchestrate all Instagram scrapers.
Takes a username as input and runs all scrapers in sequence.
"""

import sys
from profile import scrape_profile
from getMediaId import scrape_media_ids
from comments import scrape_comments
from likes import scrape_likes
from followers import scrape_followers

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
    
    # Step 1: Scrape profile posts
    print("\n[1/5] Scraping profile posts...")
    print("-" * 60)
    postid_file = scrape_profile(username)
    if not postid_file:
        print("❌ Failed to scrape profile posts. Exiting.")
        sys.exit(1)
    print(f"✅ Profile posts saved to: {postid_file}\n")
    
    # Step 2: Get media IDs
    print("\n[2/5] Extracting media IDs...")
    print("-" * 60)
    media_ids_file = scrape_media_ids(postid_file)
    if not media_ids_file:
        print("❌ Failed to extract media IDs. Exiting.")
        sys.exit(1)
    print(f"✅ Media IDs saved to: {media_ids_file}\n")
    
    # Step 3: Scrape comments
    print("\n[3/5] Scraping comments...")
    print("-" * 60)
    comments_file = scrape_comments(media_ids_file)
    if not comments_file:
        print("⚠️ Failed to scrape comments. Continuing...")
    else:
        print(f"✅ Comments saved to: {comments_file}\n")
    
    # Step 4: Scrape likes
    print("\n[4/5] Scraping likes...")
    print("-" * 60)
    likes_file = scrape_likes(media_ids_file)
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
        print(f"✅ Followers saved to: {followers_file}\n")
    
    # Summary
    print(f"\n{'='*60}")
    print("✅ Scraping process completed!")
    print(f"{'='*60}")
    print("\nGenerated files:")
    print(f"  - {postid_file}")
    if media_ids_file:
        print(f"  - {media_ids_file}")
    if comments_file:
        print(f"  - {comments_file}")
    if likes_file:
        print(f"  - {likes_file}")
    if followers_file:
        print(f"  - {followers_file}")
    print()

if __name__ == "__main__":
    main()

