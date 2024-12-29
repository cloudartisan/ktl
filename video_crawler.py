import time
import json
import argparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from login import login

def scroll_to_footer(content_container):
    """Scroll to the footer element until no more content loads, with improved tracking."""
    consecutive_failed_attempts = 0
    max_failed_attempts = 5
    num_video_cards = 0

    while consecutive_failed_attempts < max_failed_attempts:
        try:
            driver.execute_script("window.focus();")  # Ensure browser stays focused
            footer = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "bottom-footer"))
            )
            # Scroll to the footer
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'end'});", footer)
            print("Scrolled to footer.")
            time.sleep(2)  # Allow time for new content to load

            # Check if the spinner is visible
            try:
                spinner = driver.find_element(By.CSS_SELECTOR, "div.main-spinner.auto.spinner-small")
                if spinner.value_of_css_property("display") != "none":
                    WebDriverWait(driver, 10).until(
                        lambda d: spinner.value_of_css_property("display") == "none"
                    )
                    print("Spinner completed, checking for more content...")
            except Exception:
                print("Spinner not found or already completed.")

            # Re-fetch container and video cards to avoid stale references
            content_container = wait_for_content_container()
            video_cards = content_container.find_elements(By.CSS_SELECTOR, "div.col-xl-2dot4")
            if len(video_cards) == 0:
                print("No video cards found.")
                break
            elif len(video_cards) <= num_video_cards:
                consecutive_failed_attempts += 1
                print(f"No new video cards loaded. Consecutive failed attempts: {consecutive_failed_attempts}")
            else:
                num_video_cards = len(video_cards)
                print(f"Found {num_video_cards} video cards.")
                consecutive_failed_attempts = 0
        except Exception as e:
            if "stale element reference" in str(e):
                print("Encountered stale element reference. Retrying...")
                time.sleep(1)  # Small delay before retry
                continue  # Retry the loop
            else:
                print(f"Error while scrolling to footer: {e}")
                break

def wait_for_content_container():
    """Wait for the second (last) content-container div to fully load and update."""
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.content-container"))
    )
    containers = driver.find_elements(By.CSS_SELECTOR, "div.content-container")
    return containers[-1]

def extract_videos_in_section(content_container):
    """Extract video details from the current section."""
    scroll_to_footer(content_container)

    # Dynamically fetch video cards
    try:
        content_container = wait_for_content_container()
        video_cards = content_container.find_elements(By.CSS_SELECTOR, "div.col-xl-2dot4")
    except Exception as e:
        print(f"Error locating video cards: {e}")
        return

    # Track processed URLs to avoid duplicates
    processed_urls = set(video["url"] for video in all_videos)

    for card_index in range(len(video_cards)):
        try:
            # Re-fetch content container and video cards dynamically
            content_container = wait_for_content_container()
            video_cards = content_container.find_elements(By.CSS_SELECTOR, "div.col-xl-2dot4")
            card = video_cards[card_index]

            # Extract the video URL
            link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
            if link in processed_urls:
                print(f"Skipping duplicate video: {link}")
                continue

            # Extract the title
            title_element = WebDriverWait(card, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "trick-name"))
            )
            title = title_element.text.strip() if title_element.text.strip() else "Unknown Title"

            # Add to all_videos and processed set
            all_videos.append({"title": title, "url": link, "path": "/".join(current_path)})
            processed_urls.add(link)
            print(f"Found video: {title} - {link}")

        except Exception as e:
            if "stale element reference" in str(e):
                print(f"Stale element encountered for video card {card_index}. Retrying...")
                continue
            elif "element not interactable" in str(e):
                print(f"Element not interactable for video card {card_index}. Skipping...")
            else:
                print(f"Error processing video card {card_index}: {e}")

def process_menu_items(menu_items):
    """Process each menu item, including nested submenus."""
    for menu_item in menu_items:
        try:
            # Ensure menu item is visible and interactable
            ActionChains(driver).move_to_element(menu_item).perform()
            menu_item_text = menu_item.text

            print(f"Processing section: {menu_item_text}")
            current_path.append(menu_item_text)  # Update path
            menu_item.click()

            try:
                content_container = wait_for_content_container()
                extract_videos_in_section(content_container)
            except Exception as e:
                print(f"Error processing menu item '{menu_item_text}': {e}")
            finally:
                current_path.pop()  # Remove path after processing
        except Exception as e:
            print(f"Error clicking menu item: {e}")

def main():
    parser = argparse.ArgumentParser(description="Scrape video links from Kojo Trick Lab.")
    parser.add_argument("--email", required=True, help="Email for login")
    parser.add_argument("--password", required=True, help="Password for login")
    args = parser.parse_args()

    global driver
    driver = webdriver.Chrome()

    login(driver, args.email, args.password)

    global all_videos
    all_videos = []
    global current_path
    current_path = []  # Track the breadcrumb path

    # Start processing the menu
    menu_items = driver.find_elements(By.XPATH, "//nav[@id='menu']//li")
    process_menu_items(menu_items)

    # Save all videos to a JSON file in a human-readable format
    with open("crawled.json", "w") as f:
        json.dump(all_videos, f, indent=4)
    print(f"Saved {len(all_videos)} videos to crawled.json")

    driver.quit()

if __name__ == "__main__":
    main()
