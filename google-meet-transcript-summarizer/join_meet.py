# join_meet.py
from playwright.sync_api import sync_playwright
import os, time
from dotenv import load_dotenv
load_dotenv()

MEET_URL = os.environ.get("MEET_URL")  
USER_DATA_DIR = os.environ.get("USER_DATA_DIR")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_NAME = "Profile 6"
GUEST_NAME = "meeting bot"

def join_meet():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            channel="chrome",
            headless=False,
            executable_path=CHROME_EXE,
            args=[
                f"--profile-directory={PROFILE_NAME}",
                # "--use-fake-ui-for-media-stream",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-infobars",
                "--disable-features=Translate,HardwareMediaKeyHandling",
                 "--disable-blink-features=AutomationControlled"
            ]
        )
        page = ctx.new_page()
        page.goto(url = MEET_URL, wait_until="networkidle")
        time.sleep(3)

                # Try to fill name input if visible
        try:
            name_input = page.locator('input[aria-label="Your name"]')
            if name_input.is_visible():
                name_input.fill(GUEST_NAME)
                print(f"Filled guest name: {GUEST_NAME}")
        except Exception as e:
            print("No guest name input found.", e)

        # Mute mic/cam if visible
        try:
            # Try common selectors robustly
            page.locator('[aria-label*="Turn off microphone"]').first.click(timeout=2000)
        except:
            pass
        try:
            page.locator('[aria-label*="Turn off camera"]').first.click(timeout=2000)
        except:
            pass

        # Click Join now or Ask to join
        joined = False
        for sel in ['button:has-text("Join now")', '[aria-label*="Join now"]', 'button:has-text("Ask to join")']:
            try:
                page.locator(sel).click(timeout=8000)
                joined = True
                break
            except:
                pass

        if not joined:
            print("Could not find join button; check UI or sign-in.")
        else:
            print("Joined (or requested to join). Keep this window open.")
            # Prevent exit
            while True:
                time.sleep(60)

if __name__ == "__main__":
    join_meet()
