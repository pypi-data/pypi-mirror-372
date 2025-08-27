import yt_dlp
import browser_cookie3
from urllib.parse import unquote

def get_youtube_cookies():
    # Automatically fetch cookies from Chrome or Firefox
    try:
        # Get cookies from Chrome
        cookies = browser_cookie3.chrome()  # For Chrome
        # cookies = browser_cookie3.firefox()  # Uncomment for Firefox

        youtube_cookies = []
        for cookie in cookies:
            if '.youtube' in cookie.domain:
                youtube_cookies.append(cookie)

        return youtube_cookies
    except :
        try:
             cookies = browser_cookie3.firefox() 
             youtube_cookies = []
             for cookie in cookies:
                if '.youtube' in cookie.domain:
                    youtube_cookies.append(cookie)
                    
             return youtube_cookies
        except Exception as e:
            return f"Error extracting cookies: {e}"           



def save_cookies_to_netscape_format(cookies, filename='cookies.txt'):
    with open(filename, 'w') as file:
        # Write the Netscape header
        file.write("# Netscape HTTP Cookie File\n")
        file.write("# https://www.netscape.com/newsref/std/cookie_spec.html\n")
        
        # Convert each cookie to Netscape format and write it to the file
        for cookie in cookies:
            # Only keep cookies for youtube.com
            if cookie.domain and 'youtube' in cookie.domain:
                # Ensure we have all the necessary fields
                domain = cookie.domain
                path = cookie.path if cookie.path else '/'  # Default path to '/'
                secure = 'TRUE' if cookie.secure else 'FALSE'
                
                # Expiry field: Ensure it's a valid integer or 0 if None
                expires = str(int(cookie.expires)) if cookie.expires else '0'
                
                # URL-decode the cookie value to handle special characters
                value = unquote(cookie.value)

                # Validate the cookie fields before writing it
                if domain and value and len(value) > 0:
                    # Ensure the expiry is a valid integer
                    try:
                        int(expires)
                    except ValueError:
                        expires = '0'  # Default to 0 if invalid

                    # Write the cookie in the correct Netscape format
                    # Format: domain\tTRUE\tpath\tsecure\texpiry\tcookie_name\tcookie_value
                    file.write(f"{domain}\tTRUE\t{path}\t{secure}\t{expires}\t{cookie.name}\t{value}\n")
                else:
                    print(f"Skipping invalid cookie: {cookie}")



def list_formats(url):
    ydl_opts = {
        'quiet': True,  # Suppress unnecessary output
        'listformats': True,  # List all available formats
    }
    ydl_opts['cookiefile'] = "cookies.txt"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # This will list formats instead of downloading
    except Exception as e:
        return str(e)
    return None  # No error


def download_specific_format(url, format_code):
    ydl_opts = {
        'format': format_code,  # Use the selected format code
        'outtmpl': '%(title)s.%(ext)s',  # Output file name template
    }
    ydl_opts['cookiefile'] = "cookies.txt"
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return str(e)
    return "Download complete!"



def dl(url):
  
    print("Get Available Formats...")  
    list_formats(url)    
    format_code = input("Enter the format code you want to download: ")
    print(f"Downloading format {format_code}...")
    result = download_specific_format(url, format_code)
    print(result)

try:
    print("Search YT Cookies..")
    xx= get_youtube_cookies()
    print("Save YT Cookies..")
    if (xx):
         save_cookies_to_netscape_format(xx) 
except:
        print("Error: We need cookies.txt")    