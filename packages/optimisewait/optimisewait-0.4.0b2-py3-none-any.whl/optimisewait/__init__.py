import pyautogui
import time
import os
import tkinter as tk
from tkinter import font as tkFont

_default_autopath = r'C:\\'
_default_altpath = None

def set_autopath(path):
    global _default_autopath
    _default_autopath = path

def set_altpath(path):
    global _default_altpath
    _default_altpath = path

def optimiseWait(filename, dontwait=False, specreg=None, clicks=1, xoff=0, yoff=0, autopath=None, altpath=None, scrolltofind=None):
    global _default_autopath, _default_altpath
    autopath = autopath if autopath is not None else _default_autopath
    altpath = _default_altpath if altpath is None and 'altpath' not in locals() else altpath

    if not isinstance(filename, list):
        filename = [filename]
    if not isinstance(clicks, list):
        clicks = [clicks] + [1] * (len(filename) - 1)
    elif len(clicks) < len(filename):
        clicks = clicks + [1] * (len(filename) - len(clicks))
    
    if not isinstance(xoff, list):
        xoff = [xoff] * len(filename)
    elif len(xoff) < len(filename):
        xoff = xoff + [0] * (len(filename) - len(xoff))
        
    if not isinstance(yoff, list):
        yoff = [yoff] * len(filename)
    elif len(yoff) < len(filename):
        yoff = yoff + [0] * (len(filename) - len(yoff))

    while True:
        images_found = []
        
        for i, fname in enumerate(filename):
            findloc = None
            # Try main path first
            try:
                main_path = os.path.join(autopath, f'{fname}.png')
                if os.path.exists(main_path):
                    if specreg is None:
                        loc = pyautogui.locateCenterOnScreen(main_path, confidence=0.9)
                    else:
                        loc = pyautogui.locateOnScreen(main_path, region=specreg, confidence=0.9)
                    if loc: findloc = loc
            except (pyautogui.ImageNotFoundException, FileNotFoundError):
                pass
            
            # Try alt path if provided and image wasn't found in main path
            if altpath is not None and not findloc:
                try:
                    alt_path = os.path.join(altpath, f'{fname}.png')
                    if os.path.exists(alt_path):
                        if specreg is None:
                            loc = pyautogui.locateCenterOnScreen(alt_path, confidence=0.9)
                        else:
                            loc = pyautogui.locateOnScreen(alt_path, region=specreg, confidence=0.9)
                        if loc: findloc = loc
                except (pyautogui.ImageNotFoundException, FileNotFoundError):
                    continue

            if findloc is not None:
                images_found.append({'index': i, 'filename': fname, 'location': findloc})

        if images_found:
            first_found = images_found[0]
            findloc = first_found['location']
            clicked_index = first_found['index']
            
            if specreg is None:
                x, y = findloc
            else:
                x, y, width, height = findloc
            
            current_xoff = xoff[clicked_index]
            current_yoff = yoff[clicked_index]
            xmod = x + current_xoff
            ymod = y + current_yoff
            time.sleep(1)

            click_count = clicks[clicked_index]
            if click_count > 0:
                for _ in range(click_count):
                    pyautogui.click(xmod, ymod)
                    time.sleep(0.1)

        if dontwait is False:
            if images_found:
                break
            else:
                if scrolltofind == 'pageup': pyautogui.press('pageup'); time.sleep(0.5)
                elif scrolltofind == 'pagedown': pyautogui.press('pagedown'); time.sleep(0.5)
                time.sleep(1)
        else:
            if not images_found: return {'found': False, 'image': None}
            else: return {'found': True, 'image': images_found[0]['filename']}
    
    return {'found': True, 'image': images_found[0]['filename']} if images_found else {'found': False, 'image': None}

def demo_waitForBestMatch(enabled_images: list, disabled_images: list = [], timeout: int = 30, confidence: float = 0.9, autopath=None, altpath=None):
    """
    Launches a GUI to visually demonstrate the waitForBestMatch logic without clicking.
    It shows in real-time which images are being detected on screen.

    Args:
        enabled_images (list): List of image filenames for the target state.
        disabled_images (list, optional): List of image filenames for the waiting state.
        timeout (int): Maximum seconds the demo will run.
        confidence (float): The confidence level for image detection.
        autopath (str, optional): Overrides the default image path.
        altpath (str, optional): Overrides the default alternate image path.
    """
    global _default_autopath, _default_altpath
    autopath = autopath if autopath is not None else _default_autopath
    altpath = altpath if altpath is not None else _default_altpath

    # --- GUI Setup ---
    try:
        root = tk.Tk()
        root.title("OptimiseWait Demo")
        root.geometry("450x300")
        root.attributes("-topmost", True)  # Keep the window on top

        # Fonts
        title_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        status_font = tkFont.Font(family="Courier", size=11)
        
        # Widgets
        tk.Label(root, text="waitForBestMatch Live Demo", font=title_font).pack(pady=10)
        
        time_label = tk.Label(root, text="Time Elapsed: 0.0s / {}s".format(timeout), font=status_font)
        time_label.pack(pady=5)
        
        status_label = tk.Label(root, text="Status: Initializing...", font=status_font, fg="blue")
        status_label.pack(pady=10)

        tk.Label(root, text="--- Detection Status ---", font=("Helvetica", 10)).pack()
        
        enabled_label = tk.Label(root, text="[ENABLED]: Searching...", font=status_font, fg="green")
        enabled_label.pack(pady=5)

        disabled_label = tk.Label(root, text="[DISABLED]: Searching...", font=status_font, fg="orange")
        disabled_label.pack(pady=5)
        
        info_label = tk.Label(root, text=f"Confidence Threshold: {confidence}", font=("Helvetica", 8), fg="gray")
        info_label.pack(side="bottom", pady=5)

    except tk.TclError as e:
        print(f"Could not start GUI. Do you have a display environment available? Error: {e}")
        return

    # --- Main Logic Loop ---
    start_time = time.time()
    final_message = ""

    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        time_label.config(text=f"Time Elapsed: {elapsed:.1f}s / {timeout}s")
        
        # 1. Search for ENABLED images
        found_enabled_image = None
        for fname in enabled_images:
            try:
                main_path = os.path.join(autopath, f'{fname}.png')
                if os.path.exists(main_path) and pyautogui.locateOnScreen(main_path, confidence=confidence):
                    found_enabled_image = fname
                    break
                if altpath and os.path.exists(os.path.join(altpath, f'{fname}.png')) and pyautogui.locateOnScreen(os.path.join(altpath, f'{fname}.png'), confidence=confidence):
                    found_enabled_image = f"{fname} (altpath)"
                    break
            except pyautogui.ImageNotFoundException:
                continue

        if found_enabled_image:
            status_label.config(text="Status: SUCCESS! Enabled image found.", fg="green")
            enabled_label.config(text=f"[ENABLED]: DETECTED '{found_enabled_image}'")
            disabled_label.config(text="[DISABLED]: Not searched")
            final_message = "Demo finished: Enabled state was found."
            root.update()
            break # Exit the main loop

        # 2. If no enabled image, search for DISABLED images
        found_disabled_image = None
        for fname in disabled_images:
            try:
                main_path = os.path.join(autopath, f'{fname}.png')
                if os.path.exists(main_path) and pyautogui.locateOnScreen(main_path, confidence=confidence):
                    found_disabled_image = fname
                    break
                if altpath and os.path.exists(os.path.join(altpath, f'{fname}.png')) and pyautogui.locateOnScreen(os.path.join(altpath, f'{fname}.png'), confidence=confidence):
                    found_disabled_image = f"{fname} (altpath)"
                    break
            except pyautogui.ImageNotFoundException:
                continue

        # 3. Update GUI based on findings
        enabled_label.config(text="[ENABLED]: Not found")
        if found_disabled_image:
            status_label.config(text="Status: Waiting... (Disabled state visible)", fg="orange")
            disabled_label.config(text=f"[DISABLED]: DETECTED '{found_disabled_image}'")
        else:
            status_label.config(text="Status: Searching...", fg="blue")
            disabled_label.config(text="[DISABLED]: Not found")

        # Refresh the GUI window
        root.update()
        time.sleep(0.5) # Poll every half second
    
    # --- Cleanup ---
    if not final_message: # This means the loop timed out
        final_message = f"Demo finished: Timeout after {timeout} seconds."
        status_label.config(text="Status: TIMEOUT!", fg="red")
        
    print(final_message)
    root.after(4000, root.destroy) # Keep the final status visible for 4 seconds
    root.mainloop()


# --- NEW FUNCTION ---
def waitForBestMatch(enabled_images: list, disabled_images: list = [], timeout: int = 30, debug: bool = False, clicks: int = 1, xoff: int = 0, yoff: int = 0, autopath=None, altpath=None):
    """
    Waits for one of the 'enabled' images to appear on screen, while ignoring 'disabled' images.

    Args:
        enabled_images (list): List of image filenames (without .png) for the target state to click.
        disabled_images (list, optional): List of image filenames for a state that is visible but not ready.
        timeout (int): Maximum seconds to wait before giving up.
        debug (bool): If True, prints status updates to the console.
        clicks (int): Number of times to click the enabled image when found.
        xoff (int), yoff (int): X and Y offsets for the click location.
        autopath (str, optional): Overrides the default image path.
        altpath (str, optional): Overrides the default alternate image path.

    Returns:
        dict: {'found': True, 'location': (x, y)} on success,
              {'found': False, 'reason': 'timeout'} on failure.
    """
    global _default_autopath, _default_altpath
    autopath = autopath if autopath is not None else _default_autopath
    altpath = altpath if altpath is not None else _default_altpath

    start_time = time.time()
    if debug: print(f"[waitForBestMatch] Starting search. Timeout is {timeout}s.")

    while time.time() - start_time < timeout:
        # 1. Search for any of the ENABLED images
        for fname in enabled_images:
            try:
                # Try main path
                main_path = os.path.join(autopath, f'{fname}.png')
                if os.path.exists(main_path):
                    location = pyautogui.locateCenterOnScreen(main_path, confidence=0.9)
                    if location:
                        if debug: print(f"[waitForBestMatch] Found enabled image '{fname}' at {location}.")
                        x, y = location
                        pyautogui.click(x + xoff, y + yoff, clicks=clicks, interval=0.1)
                        return {'found': True, 'location': location}
                
                # Try alt path if exists
                if altpath and os.path.exists(os.path.join(altpath, f'{fname}.png')):
                    location = pyautogui.locateCenterOnScreen(os.path.join(altpath, f'{fname}.png'), confidence=0.9)
                    if location:
                        if debug: print(f"[waitForBestMatch] Found enabled image '{fname}' (in altpath) at {location}.")
                        x, y = location
                        pyautogui.click(x + xoff, y + yoff, clicks=clicks, interval=0.1)
                        return {'found': True, 'location': location}
            except pyautogui.ImageNotFoundException:
                continue # This is expected, just try the next image

        # 2. If no enabled image was found, check for DISABLED images
        found_disabled = False
        if disabled_images:
            for fname in disabled_images:
                try:
                    main_path = os.path.join(autopath, f'{fname}.png')
                    alt_path = os.path.join(altpath, f'{fname}.png') if altpath else None
                    if (os.path.exists(main_path) and pyautogui.locateOnScreen(main_path, confidence=0.9)) or \
                       (alt_path and os.path.exists(alt_path) and pyautogui.locateOnScreen(alt_path, confidence=0.9)):
                        if debug: print(f"[waitForBestMatch] Found disabled image '{fname}'. Waiting...")
                        found_disabled = True
                        break # Found a disabled state, no need to check others
                except pyautogui.ImageNotFoundException:
                    continue
        
        # 3. If neither enabled nor disabled is found, the element may not be visible yet
        if not found_disabled and debug:
            print("[waitForBestMatch] Neither enabled nor disabled state found. Still waiting...")

        time.sleep(0.5) # Poll every half second

    if debug: print(f"[waitForBestMatch] Timeout! Enabled image not found within {timeout} seconds.")
    return {'found': False, 'reason': 'timeout'}