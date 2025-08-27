"""Selenium automation for direct Google Colab interaction."""

import logging
import time
import re
import random
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

# Import stealth and undetected chrome for better bot avoidance
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False

from .session_manager import SessionManager, SessionStatus, RuntimeType
from .chrome_profile_manager import ChromeProfileManager
from .utils import retry_with_backoff, format_execution_time


class ColabSeleniumManager:
    """Manages Selenium automation for Google Colab."""
    
    # CSS Selector Constants for Colab Interface (2024-2025)
    EXECUTION_INDICATORS = [
        "colab-run-button[running='true']",
        ".cell-execution-indicator",
        "[data-testid='cell-execution-indicator']",
        ".running-indicator",
        ".spinner",
        ".loading",
        "colab-progress-bar",
        ".cell-status.running",
        ".execution-status.running"
    ]
    
    OUTPUT_SELECTORS = [
        # 2024-2025 Updated Colab output selectors
        "colab-output-area",
        "colab-output",
        "[data-testid='cell-output']",
        "[data-testid='output']",
        "[data-testid='output-area']",
        ".cell-output",
        ".output-area",
        "div.output",
        "div.output_area", 
        "div.output_wrapper",
        ".output_wrapper .output",
        ".jp-OutputArea-output",
        "div[data-mime-type]",
        "colab-output-area > div",
        "div[role='log']",
        ".output-subarea",
        "pre.output",
        ".output_text",
        "div.output_result",
        "div.stream-output",
        "div.execute_result",
        "div.display_data",
        "div.output_stdout",
        "div.output_stderr",
        # Monaco and CodeMirror output areas
        ".monaco-editor .output",
        ".CodeMirror-output",
        # Generic text containers in output areas
        "pre",
        "code",
        "span.ansi-*",
        # Jupyter/IPython style outputs
        ".text_cell_render",
        ".rendered_html"
    ]
    
    ERROR_SELECTORS = [
        # 2024-2025 Updated Colab error selectors
        ".error",
        ".traceback", 
        "[data-testid='error-output']",
        "[data-testid='error']",
        ".output_error",
        ".jp-OutputArea-output[data-mime-type*='error']",
        "div.error-output",
        "div.stderr",
        "div.output_stderr", 
        "pre.error",
        ".ansi-red-fg",
        ".ansi-red-intense-fg",
        "div[data-mime-type*='stderr']",
        "div[data-mime-type*='error']",
        ".output-error",
        "span.error",
        "div.exception",
        "div.traceback-wrapper",
        "pre.traceback",
        "div.output_subarea.output_text.output_error",
        # Common error patterns
        "*[class*='error']",
        "*[class*='Error']", 
        "*[class*='traceback']",
        "*[class*='exception']"
    ]
    
    CODE_CELL_SELECTORS = [
        "colab-cell[cell-type='code']",
        "div[data-cell-type='code']",
        ".cell[data-cell-type='code']",
        "[data-testid='code-cell']",
        ".code-cell",
        ".cell.code_cell",
        "div[role='textbox'][contenteditable='true']",
        ".notebook-cell.code-cell",
        "colab-code-cell",
        ".colab-cell-code",
        "colab-cell .inputarea",
        "div.codecell",
        ".input-container",
        "[data-cell-type='code'] .monaco-editor",
        "colab-cell[cell-type] .monaco-editor-background",
        "div[data-mprt='6']",  # Monaco editor specific
        "textarea.inputarea",
        "div.cell.jp-Cell.jp-CodeCell"
    ]
    
    ADD_CELL_SELECTORS = [
        "colab-add-cell-button",
        "button[data-testid='add-code-cell']",
        "button[aria-label*='Add code']",
        "button[title*='Add code']",
        ".add-cell-button",
        "div.add-cell button",
        "colab-toolbar-button[data-testid='add-code-cell']",
        "[data-testid='add-code-cell']",
        "button.add-cell",
        ".notebook-add-cell-button"
    ]
    
    INTERFACE_SELECTORS = [
        "colab-notebook-container",
        "[data-testid='notebook-container']",
        "div[role='main']",
        ".notebook-container",
        "#main-content",
        "colab-notebook",
        ".notebook",
        "body.notebook",
        ".colab-notebook"
    ]
    
    # Configuration Constants
    DEFAULT_OAUTH_PORT = 8080
    DEFAULT_REDIRECT_URI = 'http://localhost:8080'
    MAX_AUTH_WAIT_TIME = 300  # 5 minutes
    CELL_CREATION_WAIT = 2  # seconds
    INTERFACE_LOAD_RETRIES = 3
    EXECUTION_START_WAIT_CYCLES = 20
    EXECUTION_CHECK_INTERVAL = 1  # seconds
    
    def __init__(self, config: Dict[str, Any], session_manager: SessionManager):
        """Initialize the Selenium manager."""
        self.config = config
        self.selenium_config = config.get("selenium", {})
        self.colab_config = config.get("colab", {})
        self.session_manager = session_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize Chrome profile manager
        user_config_dir = config.get("user_config_dir")
        if not user_config_dir:
            import os
            user_config_dir = os.path.join(os.path.expanduser("~"), ".mcp-colab")
        self.profile_manager = ChromeProfileManager(user_config_dir)
        
        # Configuration
        self.browser_type = self.selenium_config.get("browser", "chrome").lower()
        self.headless = self.selenium_config.get("headless", False)
        self.timeout = self.selenium_config.get("timeout", 30)
        self.implicit_wait = self.selenium_config.get("implicit_wait", 10)
        self.page_load_timeout = self.selenium_config.get("page_load_timeout", 30)
        self.execution_timeout = self.colab_config.get("execution_timeout", 300)
        
        # Profile configuration
        self.profile_config = self.selenium_config.get("profile", {})
        self.use_persistent_profile = self.profile_config.get("use_persistent_profile", True)
        self.profile_name = self.profile_config.get("profile_name", "default")
        
        # Colab URLs
        self.base_url = self.colab_config.get("base_url", "https://colab.research.google.com")
        
        # WebDriver instance
        self.driver: Optional[webdriver.Remote] = None
        self.current_notebook_id: Optional[str] = None
    
    def _create_driver(self) -> webdriver.Remote:
        """Create and configure WebDriver instance with anti-detection measures."""
        try:
            if self.browser_type == "chrome":
                return self._create_chrome_driver()
            elif self.browser_type == "firefox":
                return self._create_firefox_driver()
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
                
        except Exception as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise
    
    def _create_chrome_driver(self) -> webdriver.Remote:
        """Create Chrome WebDriver with profile management."""
        use_undetected = self.selenium_config.get("use_undetected_chrome", False)
        
        # Get additional Chrome options from config
        additional_options = []
        if self.headless:
            additional_options.extend(["--headless=new", "--disable-gpu"])
        
        # Anti-detection options from config
        anti_detection_config = self.selenium_config.get("anti_detection", {})
        if anti_detection_config.get("disable_images", False):
            additional_options.append("--disable-images")
        if anti_detection_config.get("custom_user_agent", True):
            additional_options.append("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Try undetected-chromedriver first for better stealth
        if UNDETECTED_CHROME_AVAILABLE and not self.headless and use_undetected:
            return self._create_undetected_chrome_driver(additional_options)
        else:
            return self._create_regular_chrome_driver(additional_options)
    
    def _create_undetected_chrome_driver(self, additional_options: List[str]) -> webdriver.Remote:
        """Create undetected Chrome driver."""
        self.logger.info("Using undetected-chromedriver for better stealth")
        
        options = uc.ChromeOptions()
        
        # Use profile manager for consistent profile handling
        if self.use_persistent_profile:
            profile_path = self.profile_manager.get_profile_path(self.profile_name)
            options.add_argument(f"--user-data-dir={profile_path}")
            self.logger.info(f"Using persistent Chrome profile: {profile_path}")
        
        # Basic options for stability
        basic_options = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--start-maximized",
            "--disable-blink-features=AutomationControlled"
        ]
        
        for option in basic_options + additional_options:
            options.add_argument(option)
        
        # Anti-detection experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Create undetected chrome driver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Execute script to remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _create_regular_chrome_driver(self, additional_options: List[str]) -> webdriver.Remote:
        """Create regular Chrome driver with stealth measures."""
        self.logger.info("Using regular Chrome WebDriver with stealth measures")
        
        # Use profile manager to create Chrome options
        if self.use_persistent_profile:
            options = self.profile_manager.create_chrome_options(
                profile_name=self.profile_name,
                additional_options=additional_options
            )
        else:
            options = webdriver.ChromeOptions()
            for option in additional_options:
                options.add_argument(option)
        
        # Find Chrome binary
        self._set_chrome_binary_location(options)
        
        # Create Chrome service
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Apply stealth if available
        if STEALTH_AVAILABLE and self.selenium_config.get("use_stealth", False):
            stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
        
        # Execute script to remove automation indicators
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def _set_chrome_binary_location(self, options: webdriver.ChromeOptions) -> None:
        """Set Chrome binary location if needed."""
        import shutil
        import os
        
        chrome_path = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chromium")
        if chrome_path:
            options.binary_location = chrome_path
            self.logger.info(f"Chrome binary found at: {chrome_path}")
        else:
            # Windows için varsayılan Chrome yolları
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', ''))
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    options.binary_location = path
                    self.logger.info(f"Chrome binary found at: {path}")
                    break
    
    def _create_firefox_driver(self) -> webdriver.Remote:
        """Create Firefox WebDriver."""
        options = webdriver.FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        
        # Anti-detection for Firefox
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        # Configure timeouts
        driver.implicitly_wait(self.implicit_wait)
        driver.set_page_load_timeout(self.page_load_timeout)
        
        # Add random delay to appear more human-like
        time.sleep(random.uniform(1, 3))
        
        self.logger.info("Created Firefox WebDriver instance")
        return driver
    
    def _ensure_driver(self) -> None:
        """Ensure WebDriver is available and functional."""
        if self.driver is None:
            self.driver = self._create_driver()
        else:
            try:
                # Test if driver is still responsive
                self.driver.current_url
            except WebDriverException:
                self.logger.warning("WebDriver became unresponsive, creating new instance")
                self._close_driver()
                self.driver = self._create_driver()
    
    def _close_driver(self) -> None:
        """Close WebDriver instance."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def get_profile_info(self) -> Dict[str, Any]:
        """Get information about the current Chrome profile configuration."""
        if self.use_persistent_profile:
            return self.profile_manager.get_profile_info(self.profile_name)
        else:
            return {
                "persistent_profile_enabled": False,
                "profile_directory": None,
                "profile_exists": False,
                "profile_size_mb": 0,
                "name": "temporary",
                "metadata": {}
            }
    
    def clear_profile(self, profile_name: str = None) -> bool:
        """Clear the persistent Chrome profile data."""
        try:
            if not self.use_persistent_profile:
                self.logger.warning("Persistent profile is not enabled")
                return False
            
            # Use specified profile name or current profile
            target_profile = profile_name or self.profile_name
            
            # Close driver first if it's running
            if self.driver:
                self._close_driver()
            
            # Use profile manager to clear profile
            return self.profile_manager.clear_profile(target_profile)
            
        except Exception as e:
            self.logger.error(f"Error clearing profile: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all available Chrome profiles."""
        return self.profile_manager.list_profiles()
    
    def optimize_profile(self, profile_name: str = None) -> bool:
        """Optimize Chrome profile by cleaning temporary files."""
        if not self.use_persistent_profile:
            self.logger.warning("Persistent profile is not enabled")
            return False
        
        target_profile = profile_name or self.profile_name
        return self.profile_manager.optimize_profile(target_profile)
    
    def backup_profile(self, profile_name: str = None, backup_name: str = None) -> bool:
        """Create a backup of Chrome profile."""
        if not self.use_persistent_profile:
            self.logger.warning("Persistent profile is not enabled")
            return False
        
        target_profile = profile_name or self.profile_name
        return self.profile_manager.backup_profile(target_profile, backup_name)
    
    def restore_profile(self, backup_name: str, target_name: str = None) -> bool:
        """Restore Chrome profile from backup."""
        if not self.use_persistent_profile:
            self.logger.warning("Persistent profile is not enabled")
            return False
        
        target_profile = target_name or self.profile_name
        return self.profile_manager.restore_profile(backup_name, target_profile)
    
    def get_profiles_summary(self) -> Dict[str, Any]:
        """Get summary of all profiles and their usage."""
        profiles = self.list_profiles()
        total_size = self.profile_manager.get_total_profiles_size()
        
        return {
            "total_profiles": len(profiles),
            "total_size_mb": total_size,
            "current_profile": self.profile_name if self.use_persistent_profile else "temporary",
            "persistent_enabled": self.use_persistent_profile,
            "profiles": profiles
        }
    
    @retry_with_backoff(max_retries=3, delay=2.0)
    def open_notebook(self, notebook_id: str) -> bool:
        """Open a Colab notebook in the browser."""
        try:
            self._ensure_driver()
            
            # Construct Colab URL
            notebook_url = f"{self.base_url}/drive/{notebook_id}"
            
            self.logger.info(f"Opening notebook: {notebook_url}")
            self.driver.get(notebook_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if we need to sign in
            if "accounts.google.com" in self.driver.current_url:
                self.logger.warning("Google sign-in required - please authenticate manually")
                self.logger.info("Browser will remain open for manual authentication")
                self.logger.info("After signing in, the session will be saved for future use")
                
                # Wait for user to complete authentication
                max_auth_wait = 300  # 5 minutes
                auth_start_time = time.time()
                
                while time.time() - auth_start_time < max_auth_wait:
                    current_url = self.driver.current_url
                    if "accounts.google.com" not in current_url and "colab.research.google.com" in current_url:
                        self.logger.info("Authentication completed successfully!")
                        break
                    time.sleep(2)
                else:
                    self.logger.error("Authentication timeout - please try again")
                    return False
            
            # Wait for Colab interface to load
            self._wait_for_colab_interface()
            
            self.current_notebook_id = notebook_id
            self.session_manager.update_session_status(notebook_id, SessionStatus.CONNECTED)
            
            self.logger.info(f"Successfully opened notebook: {notebook_id}")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout waiting for notebook to load")
            self.session_manager.update_session_status(notebook_id, SessionStatus.ERROR, "Timeout loading notebook")
            return False
        except Exception as e:
            self.logger.error(f"Error opening notebook: {e}")
            self.session_manager.update_session_status(notebook_id, SessionStatus.ERROR, str(e))
            return False
    
    def _wait_for_colab_interface(self) -> None:
        """Wait for Colab interface elements to load."""
        # Wait for any of the interface elements
        for attempt in range(3):
            try:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.any_of(*[
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        for selector in self.INTERFACE_SELECTORS
                    ])
                )
                break
            except TimeoutException:
                if attempt < 2:
                    self.logger.warning(f"Interface loading attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
                else:
                    raise
        
        # Wait for JavaScript to load and interface to be interactive
        WebDriverWait(self.driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # Additional wait for dynamic content and React components
        time.sleep(3)
    
    def _find_code_cells(self) -> List:
        """Find all code cells in the notebook."""
        try:
            for selector in self.CODE_CELL_SELECTORS:
                try:
                    cells = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cells:
                        self.logger.debug(f"Found {len(cells)} code cells using selector: {selector}")
                        return cells
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no cells found, try to find any editable elements
            fallback_selectors = [
                "div[contenteditable='true']",
                "textarea",
                ".CodeMirror-code",
                ".monaco-editor"
            ]
            
            for selector in fallback_selectors:
                try:
                    cells = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if cells:
                        self.logger.warning(f"Using fallback selector: {selector}")
                        return cells
                except Exception:
                    continue
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error finding code cells: {e}")
            return []
    
    def _create_new_code_cell(self) -> Optional[Any]:
        """Create a new code cell."""
        try:
            for selector in self.ADD_CELL_SELECTORS:
                try:
                    add_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # Scroll to button if needed
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
                    time.sleep(0.5)
                    
                    # Click using JavaScript to avoid interception
                    self.driver.execute_script("arguments[0].click();", add_button)
                    time.sleep(2)  # Wait for cell to be created
                    
                    # Return the newly created cell
                    cells = self._find_code_cells()
                    if cells:
                        return cells[-1]  # Return the last cell (newly created)
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    self.logger.debug(f"Failed to click add cell button with selector {selector}: {e}")
                    continue
            
            # Alternative methods to create cells
            alternatives = [
                # Keyboard shortcuts
                lambda: self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + Keys.ALT + "n"),
                lambda: self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "m", "b"),
                # Try clicking on notebook area first, then shortcut
                lambda: (
                    self.driver.find_element(By.TAG_NAME, "body").click(),
                    time.sleep(0.5),
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + Keys.ALT + "n")
                )
            ]
            
            for alternative in alternatives:
                try:
                    alternative()
                    time.sleep(2)
                    cells = self._find_code_cells()
                    if cells:
                        return cells[-1]
                except Exception as e:
                    self.logger.debug(f"Alternative method failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating new code cell: {e}")
            return None
    
    def execute_code(self, notebook_id: str, code: str) -> Dict[str, Any]:
        """Execute code in a Colab notebook with improved error handling and timeout management."""
        execution_start_time = time.time()
        cell = None
        execution_result = None
        
        try:
            # Ensure notebook is open
            if self.current_notebook_id != notebook_id:
                if not self.open_notebook(notebook_id):
                    return self._create_error_result("Failed to open notebook", execution_start_time)
            
            # Determine if this might be a long-running operation
            is_long_running = self._is_potentially_long_running(code)
            
            # Mark execution start in session manager
            self.session_manager.mark_execution_start(
                notebook_id, 
                is_long_running=is_long_running, 
                custom_timeout=self.execution_timeout
            )
            
            # Find or create a code cell with timeout
            try:
                cells = self._find_code_cells()
                if not cells:
                    cell = self._create_new_code_cell()
                    if not cell:
                        return self._create_error_result("Could not find or create code cell", execution_start_time)
                else:
                    cell = cells[-1]  # Use the last cell
            except Exception as e:
                return self._create_error_result(f"Failed to access code cell: {str(e)}", execution_start_time)
            
            # Enter code with proper error handling
            try:
                self._enter_code_in_cell(cell, code)
                self.logger.debug("Code entered successfully")
            except Exception as e:
                return self._create_error_result(f"Failed to enter code: {str(e)}", execution_start_time)
            
            # Execute the cell with comprehensive error handling
            try:
                execution_result = self._execute_cell_with_timeout(cell)
            except Exception as e:
                return self._create_error_result(f"Cell execution failed: {str(e)}", execution_start_time)
            
            # Mark execution as completed
            self.session_manager.mark_execution_end(notebook_id)
            
            # Validate and format result
            if not isinstance(execution_result, dict):
                execution_result = {
                    'output': str(execution_result) if execution_result else '',
                    'error': None,
                    'execution_time': time.time() - execution_start_time
                }
            
            # Determine success based on whether there's an error
            success = execution_result.get('error') is None
            
            # Log execution result
            if success:
                output_preview = str(execution_result.get('output', ''))[:100]
                self.logger.info(f"Code execution successful. Output preview: {output_preview}{'...' if len(output_preview) >= 100 else ''}")
            else:
                error_preview = str(execution_result.get('error', ''))[:100]
                self.logger.warning(f"Code execution completed with error: {error_preview}{'...' if len(error_preview) >= 100 else ''}")
            
            return {
                'success': success,
                'output': execution_result.get('output', ''),
                'error': execution_result.get('error'),
                'execution_time': execution_result.get('execution_time', time.time() - execution_start_time),
                'cell_type': 'code',
                'notebook_id': notebook_id,
                'is_long_running': is_long_running
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error executing code: {e}", exc_info=True)
            return self._create_error_result(f"Unexpected execution error: {str(e)}", execution_start_time)
        
        finally:
            # Always ensure execution tracking is cleaned up
            try:
                self.session_manager.mark_execution_end(notebook_id)
            except:
                pass  # Don't let cleanup errors affect the response
            
            total_execution_time = time.time() - execution_start_time
            self.logger.info(f"Code execution completed in {total_execution_time:.2f} seconds")
    
    def _is_potentially_long_running(self, code: str) -> bool:
        """Determine if code is potentially long-running based on patterns."""
        long_running_indicators = [
            'time.sleep',
            'input(',
            'plt.show()',
            'while true',
            'download',
            'fit(',
            'train(',
            '.fit_transform(',
            'gridsearchcv',
            'cross_val_score',
        ]
        
        code_lower = code.lower()
        
        # Check for simple indicators
        for indicator in long_running_indicators:
            if indicator in code_lower:
                return True
        
        # Check for loops with large ranges
        if 'for' in code_lower and 'range(' in code_lower:
            if '1000' in code or '10000' in code:
                return True
        
        return False
    
    def _create_error_result(self, error_message: str, start_time: float) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            'success': False,
            'output': '',
            'error': error_message,
            'execution_time': time.time() - start_time,
            'cell_type': 'code'
        }
    
    def _enter_code_in_cell(self, cell, code: str) -> None:
        """Enter code into a cell."""
        try:
            # Scroll the cell into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cell)
            time.sleep(0.5)
            
            # Try multiple strategies to focus and enter code
            strategies = [
                lambda: self._enter_code_strategy_1(cell, code),  # Click and type
                lambda: self._enter_code_strategy_2(cell, code),  # JavaScript focus
                lambda: self._enter_code_strategy_3(cell, code),  # Find Monaco editor
                lambda: self._enter_code_strategy_4(cell, code),  # Find textarea
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    self.logger.debug(f"Trying code entry strategy {i + 1}")
                    strategy()
                    self.logger.debug(f"Successfully entered code using strategy {i + 1}")
                    return
                except Exception as e:
                    self.logger.debug(f"Strategy {i + 1} failed: {e}")
                    continue
            
            raise Exception("All code entry strategies failed")
            
        except Exception as e:
            self.logger.error(f"Error entering code in cell: {e}")
            raise
    
    def _enter_code_strategy_1(self, cell, code: str) -> None:
        """Strategy 1: Direct click and send keys."""
        # Try to click on the cell
        try:
            cell.click()
        except:
            # If click is intercepted, try JavaScript click
            self.driver.execute_script("arguments[0].click();", cell)
        
        time.sleep(0.5)
        
        # Clear and enter code
        cell.send_keys(Keys.CONTROL + "a")
        cell.send_keys(Keys.DELETE)
        cell.send_keys(code)
    
    def _enter_code_strategy_2(self, cell, code: str) -> None:
        """Strategy 2: Use JavaScript to focus and set value."""
        # Focus using JavaScript
        self.driver.execute_script("arguments[0].focus();", cell)
        time.sleep(0.3)
        
        # Try to set value directly if possible
        try:
            self.driver.execute_script("arguments[0].value = arguments[1];", cell, code)
            # Trigger input events
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, cell)
        except:
            # Fallback to send_keys
            cell.clear()
            cell.send_keys(code)
    
    def _enter_code_strategy_3(self, cell, code: str) -> None:
        """Strategy 3: Find Monaco editor within cell."""
        # Look for Monaco editor elements
        monaco_selectors = [
            ".monaco-editor textarea",
            ".inputarea",
            "textarea[data-mprt]",
            ".monaco-mouse-cursor-text"
        ]
        
        for selector in monaco_selectors:
            try:
                editor_element = cell.find_element(By.CSS_SELECTOR, selector)
                if editor_element:
                    # Click on editor
                    self.driver.execute_script("arguments[0].click();", editor_element)
                    time.sleep(0.3)
                    
                    # Clear and enter code
                    editor_element.send_keys(Keys.CONTROL + "a")
                    editor_element.send_keys(code)
                    return
            except:
                continue
        
        raise Exception("Monaco editor not found")
    
    def _enter_code_strategy_4(self, cell, code: str) -> None:
        """Strategy 4: Find any editable element within cell."""
        # Look for any editable elements
        editable_selectors = [
            "textarea",
            "[contenteditable='true']",
            "input[type='text']",
            "div[role='textbox']"
        ]
        
        for selector in editable_selectors:
            try:
                editable_elements = cell.find_elements(By.CSS_SELECTOR, selector)
                for element in editable_elements:
                    if element.is_displayed() and element.is_enabled():
                        # Use Actions class for more reliable interaction
                        actions = ActionChains(self.driver)
                        actions.move_to_element(element)
                        actions.click(element)
                        actions.perform()
                        time.sleep(0.3)
                        
                        # Clear and enter code
                        element.send_keys(Keys.CONTROL + "a")
                        element.send_keys(code)
                        return
            except:
                continue
        
        raise Exception("No editable element found")
    
    def _execute_cell_with_timeout(self, cell) -> Dict[str, Any]:
        """Execute a code cell with comprehensive timeout and error handling."""
        execution_start_time = time.time()
        max_total_time = self.execution_timeout + 60  # Extra buffer for execution setup
        
        try:
            start_time = time.time()
            
            # Multiple execution strategies with timeout check
            execution_strategies = [
                lambda: self._execute_strategy_shift_enter(cell),
                lambda: self._execute_strategy_ctrl_enter(cell),
                lambda: self._execute_strategy_run_button(cell),
                lambda: self._execute_strategy_javascript(cell),
            ]
            
            executed = False
            execution_error = None
            
            for i, strategy in enumerate(execution_strategies):
                # Check if we've exceeded total time limit before attempting each strategy
                if time.time() - execution_start_time > max_total_time:
                    self.logger.warning(f"Total execution time limit exceeded before strategy {i+1}")
                    break
                    
                try:
                    self.logger.debug(f"Attempting execution strategy {i + 1}")
                    strategy()
                    executed = True
                    self.logger.debug(f"Successfully executed using strategy {i + 1}")
                    break
                except Exception as e:
                    execution_error = str(e)
                    self.logger.debug(f"Execution strategy {i + 1} failed: {e}")
                    continue
            
            if not executed:
                # If all strategies failed, return immediately with the last error
                self.logger.error("All execution strategies failed")
                return {
                    'output': '',
                    'error': f'Failed to execute cell: {execution_error or "All execution strategies failed"}',
                    'execution_time': time.time() - start_time
                }
            
            # Wait for execution to complete with better timeout and error handling
            try:
                # First wait for execution to complete
                output, error = self._wait_for_execution_complete_with_timeout()
                
                # If no output found, try additional waiting and extraction strategies
                if not output and not error:
                    self.logger.debug("No immediate output found, trying extended extraction...")
                    
                    # Wait a bit longer for output to appear
                    for wait_attempt in range(3):  # Try 3 times with increasing delays
                        time.sleep(1 + wait_attempt)  # 1s, 2s, 3s delays
                        
                        # Try extraction again
                        temp_output, temp_error = self._extract_cell_output_safe()
                        if temp_output or temp_error:
                            output, error = temp_output, temp_error
                            self.logger.debug(f"Found output on attempt {wait_attempt + 1}")
                            break
                    
                    # If still no output, try one more comprehensive search
                    if not output and not error:
                        self.logger.debug("Trying final comprehensive output search...")
                        output, error = self._extract_all_possible_outputs()
                
                # Additional validation of results
                if error:
                    self.logger.info(f"Execution completed with error: {error[:100]}..." if len(str(error)) > 100 else f"Execution completed with error: {error}")
                elif output:
                    self.logger.info(f"Execution completed successfully with output ({len(str(output))} chars)")
                else:
                    self.logger.info("Execution completed with no output")
                    
            except Exception as e:
                self.logger.error(f"Error during execution wait: {e}")
                # Try to extract any available output as fallback
                try:
                    output, error = self._extract_cell_output_safe()
                    if not error:
                        error = f"Execution monitoring failed: {str(e)}"
                except Exception as fallback_error:
                    self.logger.error(f"Fallback output extraction also failed: {fallback_error}")
                    output, error = '', f"Execution failed and output extraction failed: {str(e)}"
            
            execution_time = time.time() - start_time
            
            # Ensure we don't exceed the maximum time limit
            if execution_time > self.execution_timeout:
                warning_msg = f"Execution time ({execution_time:.1f}s) exceeded configured timeout ({self.execution_timeout}s)"
                self.logger.warning(warning_msg)
                if not error:
                    error = f"Execution timeout after {self.execution_timeout} seconds - code may still be running in background"
            
            return {
                'output': output or '',
                'error': error,
                'execution_time': execution_time
            }
            
        except Exception as e:
            self.logger.error(f"Unexpected error in cell execution: {e}", exc_info=True)
            return {
                'output': '',
                'error': f'Unexpected execution error: {str(e)}',
                'execution_time': time.time() - execution_start_time
            }
    
    def _execute_strategy_shift_enter(self, cell) -> None:
        """Execute cell using Shift+Enter."""
        cell.send_keys(Keys.SHIFT + Keys.ENTER)
    
    def _execute_strategy_ctrl_enter(self, cell) -> None:
        """Execute cell using Ctrl+Enter."""
        cell.send_keys(Keys.CONTROL + Keys.ENTER)
    
    def _execute_strategy_run_button(self, cell) -> None:
        """Execute cell by clicking run button."""
        run_button_selectors = [
            "colab-run-button",
            "[data-testid='run-cell-button']",
            "button[aria-label*='Run']",
            ".run-button",
            "iron-icon[icon='av:play-arrow']",
            "button[title*='Run']"
        ]
        
        # Look for run button near the cell
        for selector in run_button_selectors:
            try:
                # First try to find button within cell
                run_button = cell.find_element(By.CSS_SELECTOR, selector)
                if run_button and run_button.is_displayed():
                    self.driver.execute_script("arguments[0].click();", run_button)
                    return
            except:
                try:
                    # Try to find button in the toolbar or nearby
                    run_buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in run_buttons:
                        if button.is_displayed() and button.is_enabled():
                            self.driver.execute_script("arguments[0].click();", button)
                            return
                except:
                    continue
        
        raise Exception("Run button not found")
    
    def _execute_strategy_javascript(self, cell) -> None:
        """Execute cell using JavaScript events."""
        # Try to trigger execution via JavaScript
        self.driver.execute_script("""
            // Try various methods to execute the cell
            var cell = arguments[0];
            
            // Method 1: Dispatch keyboard events
            var shiftEnterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                shiftKey: true,
                bubbles: true
            });
            cell.dispatchEvent(shiftEnterEvent);
            
            // Method 2: Try to find and trigger Colab's execution function
            if (window.colab && window.colab.kernel) {
                try {
                    window.colab.kernel.execute();
                } catch (e) {}
            }
            
            // Method 3: Dispatch custom execution event
            var executeEvent = new CustomEvent('execute-cell', { bubbles: true });
            cell.dispatchEvent(executeEvent);
        """, cell)
    
    def _wait_for_execution_complete_with_timeout(self) -> Tuple[str, Optional[str]]:
        """Wait for cell execution to complete with improved timeout handling."""
        try:
            max_wait_time = self.execution_timeout
            start_time = time.time()
            
            # Wait for execution to start (indicator appears) - max 15 seconds
            execution_started = False
            start_check_timeout = 15
            start_check_start = time.time()
            
            while time.time() - start_check_start < start_check_timeout:
                # Check if total time limit is exceeded
                if time.time() - start_time > max_wait_time:
                    self.logger.warning("Total timeout exceeded while waiting for execution to start")
                    break
                    
                for indicator_selector in self.EXECUTION_INDICATORS:
                    try:
                        indicators = self.driver.find_elements(By.CSS_SELECTOR, indicator_selector)
                        if indicators and any(indicator.is_displayed() for indicator in indicators):
                            execution_started = True
                            self.logger.debug(f"Execution started, found indicator: {indicator_selector}")
                            break
                    except Exception:
                        continue
                
                if execution_started:
                    break
                
                time.sleep(0.5)
            
            # If no execution indicator found, assume execution started immediately
            if not execution_started:
                self.logger.info("No execution indicator found, assuming immediate execution")
                time.sleep(2)  # Brief wait for potential immediate execution
            
            # Wait for execution to complete with better monitoring
            execution_completed = False
            completion_check_start = time.time()
            consecutive_clear_checks = 0
            required_clear_checks = 2  # Reduced from 3 to 2 for faster response
            last_output_check = time.time()
            output_check_interval = 5  # Check output every 5 seconds during long executions
            
            while time.time() - completion_check_start < max_wait_time:
                current_time = time.time()
                
                # Periodically extract output to detect errors early
                if current_time - last_output_check >= output_check_interval:
                    try:
                        temp_output, temp_error = self._extract_cell_output_safe()
                        if temp_error and "error" in temp_error.lower():
                            self.logger.info("Early error detection - stopping execution wait")
                            return temp_output, temp_error
                        last_output_check = current_time
                    except:
                        pass  # Continue monitoring
                
                # Check if any execution indicators are still present
                indicators_present = False
                for indicator_selector in self.EXECUTION_INDICATORS:
                    try:
                        indicators = self.driver.find_elements(By.CSS_SELECTOR, indicator_selector)
                        if indicators and any(indicator.is_displayed() for indicator in indicators):
                            indicators_present = True
                            break
                    except Exception:
                        continue
                
                if not indicators_present:
                    consecutive_clear_checks += 1
                    if consecutive_clear_checks >= required_clear_checks:
                        execution_completed = True
                        self.logger.debug(f"Execution completed after {consecutive_clear_checks} clear checks")
                        break
                else:
                    consecutive_clear_checks = 0  # Reset counter if indicators are found
                
                time.sleep(1)  # Check every second
            
            if not execution_completed:
                self.logger.warning(f"Execution timeout after {max_wait_time} seconds - extracting available output")
            
            # Always try to extract final output
            output, error = self._extract_cell_output_safe()
            
            # If we timed out and got no meaningful output, provide helpful message
            if not execution_completed and not output and not error:
                error = f"Execution timeout after {max_wait_time} seconds. Code may still be running in background. Check Colab notebook for results."
            
            return output, error
            
        except Exception as e:
            self.logger.error(f"Error waiting for execution: {e}", exc_info=True)
            # Always try to extract what we can
            try:
                output, error = self._extract_cell_output_safe()
                if not error:
                    error = f"Execution monitoring failed: {str(e)}"
                return output, error
            except Exception as extract_error:
                self.logger.error(f"Fallback extraction also failed: {extract_error}")
                return "", f"Execution monitoring and output extraction failed: {str(e)}"
    
    def _extract_all_possible_outputs(self) -> Tuple[str, Optional[str]]:
        """Final fallback method to extract any possible output from the page."""
        try:
            self.logger.debug("Starting comprehensive fallback output extraction...")
            
            all_text_content = []
            error_content = None
            
            # Strategy 1: Get all text from the page and filter for meaningful content
            try:
                all_text = self.driver.execute_script("""
                    var allText = [];
                    var walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    
                    var node;
                    while (node = walker.nextNode()) {
                        var parent = node.parentElement;
                        if (parent && parent.offsetParent !== null) {  // Visible element
                            var text = node.textContent.trim();
                            if (text.length > 2 && !text.match(/^[\s\n\r]*$/)) {
                                allText.push(text);
                            }
                        }
                    }
                    return allText;
                """)
                
                if all_text and isinstance(all_text, list):
                    # Filter for likely output content
                    for text in all_text:
                        text_str = str(text).strip()
                        # Look for actual content (not UI elements)
                        if (text_str and len(text_str) > 3 and
                            not any(ui_text in text_str.lower() for ui_text in [
                                'colab', 'google', 'notebook', 'cell', 'run', 'edit', 'view',
                                'file', 'tools', 'help', 'share', 'connect', 'ram', 'disk'
                            ])):
                            all_text_content.append(text_str)
                            
            except Exception as js_error:
                self.logger.debug(f"JavaScript text extraction failed: {js_error}")
            
            # Strategy 2: Look for any elements that might contain output
            output_candidates = []
            try:
                # Try different element types that might contain output
                candidate_selectors = [
                    "div:not([class*='menu']):not([class*='toolbar']):not([class*='header'])",
                    "p", "span", "pre", "code", "blockquote"
                ]
                
                for selector in candidate_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if text and len(text) > 5:
                                # Check if this looks like output content
                                lower_text = text.lower()
                                if (not any(ui_word in lower_text for ui_word in [
                                    'menu', 'button', 'click', 'select', 'choose', 'toolbar'
                                ]) and
                                    any(output_indicator in lower_text for output_indicator in [
                                        'print', 'result', 'output', 'error', 'success', 'complete',
                                        ':', '=', 'true', 'false', 'none', 'warning'
                                    ]) or
                                    # Or if it's a simple value/result
                                    text.replace(' ', '').replace('\n', '').isdigit() or
                                    text.count('\n') > 0):  # Multi-line content
                                    output_candidates.append(text)
                                    
                                    # Check for error patterns
                                    if any(error_word in lower_text for error_word in [
                                        'error', 'exception', 'traceback', 'failed', 'invalid'
                                    ]):
                                        error_content = text
                        
            except Exception as element_error:
                self.logger.debug(f"Element-based extraction failed: {element_error}")
            
            # Combine and clean results
            all_outputs = all_text_content + output_candidates
            
            if all_outputs:
                # Remove duplicates and very short content
                unique_outputs = list(dict.fromkeys([out for out in all_outputs if len(out.strip()) > 5]))
                
                # Take the most relevant outputs (last few, which are likely the most recent)
                relevant_outputs = unique_outputs[-5:] if len(unique_outputs) > 5 else unique_outputs
                
                final_output = '\n'.join(relevant_outputs).strip()
                
                if final_output:
                    self.logger.debug(f"Fallback extraction found: {final_output[:150]}...")
                    return final_output, error_content
            
            # If still nothing, return empty
            self.logger.debug("No content found in comprehensive extraction")
            return "", error_content
            
        except Exception as e:
            self.logger.error(f"Comprehensive extraction failed: {e}")
            return "", f"Extraction error: {str(e)}"

    def _extract_cell_output_safe(self) -> Tuple[str, Optional[str]]:
        """Safely extract output and error from cell execution with comprehensive approach."""
        try:
            output_text = ""
            error_text = None
            
            # Increased timeout for more thorough extraction
            extraction_timeout = 12  # Increased to allow more comprehensive search
            extraction_start = time.time()
            
            self.logger.debug("Starting comprehensive output extraction...")
            
            # Strategy 1: Try standard output selectors
            output_elements = []
            for i, selector in enumerate(self.OUTPUT_SELECTORS):
                if time.time() - extraction_start > extraction_timeout:
                    self.logger.debug("Output extraction timeout - breaking selector loop")
                    break
                    
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        # Get all visible elements, not just the last one
                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            output_elements.extend(visible_elements)
                            self.logger.debug(f"Found {len(visible_elements)} output elements using selector: {selector}")
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Strategy 2: If no standard outputs found, search more broadly
            if not output_elements:
                self.logger.debug("No standard outputs found, trying broader search...")
                broader_selectors = [
                    "*[id*='output']",
                    "*[class*='output']", 
                    "*[data-testid*='output']",
                    "div[role='log']",
                    "div[role='region']",
                    "pre",
                    "code",
                    "span"
                ]
                
                for selector in broader_selectors:
                    if time.time() - extraction_start > extraction_timeout:
                        break
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        visible_elements = [elem for elem in elements 
                                          if elem.is_displayed() and elem.text.strip()]
                        if visible_elements:
                            output_elements.extend(visible_elements[:5])  # Limit to first 5 to avoid noise
                            self.logger.debug(f"Found {len(visible_elements)} broader elements using: {selector}")
                            break
                    except:
                        continue
            
            # Extract text from found elements
            if output_elements:
                all_output_texts = []
                
                for element in output_elements:
                    if time.time() - extraction_start > extraction_timeout:
                        break
                        
                    # Check for errors first
                    if not error_text:
                        for error_selector in self.ERROR_SELECTORS:
                            try:
                                error_elements = element.find_elements(By.CSS_SELECTOR, error_selector)
                                if error_elements and error_elements[0].is_displayed():
                                    potential_error = error_elements[0].text.strip()
                                    if potential_error and len(potential_error) > 5:  # Meaningful error text
                                        error_text = potential_error
                                        self.logger.debug(f"Found error using selector: {error_selector}")
                                        break
                            except:
                                continue
                    
                    # Extract regular text
                    try:
                        element_text = element.text.strip()
                        if element_text and len(element_text) > 0:
                            all_output_texts.append(element_text)
                    except:
                        # Fallback to textContent
                        try:
                            element_text = element.get_attribute('textContent')
                            if element_text and element_text.strip():
                                all_output_texts.append(element_text.strip())
                        except:
                            continue
                
                # Process collected texts
                if all_output_texts:
                    # Remove duplicates while preserving order
                    unique_texts = []
                    seen_texts = set()
                    for text in all_output_texts:
                        if text not in seen_texts and len(text.strip()) > 0:
                            unique_texts.append(text)
                            seen_texts.add(text)
                    
                    # Combine all unique texts
                    combined_output = '\n'.join(unique_texts).strip()
                    
                    # Clean up the output
                    if combined_output:
                        lines = combined_output.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            line_clean = line.strip()
                            # Skip empty lines and execution indicators
                            if (line_clean and 
                                not any(indicator in line_clean.lower() for indicator in 
                                       ['executing', 'running', 'loading', 'please wait', 'connecting']) and
                                not line_clean.startswith('...')): # Skip ellipsis indicators
                                cleaned_lines.append(line)
                        
                        output_text = '\n'.join(cleaned_lines).strip()
                        
                        self.logger.debug(f"Extracted output ({len(output_text)} chars): {output_text[:100]}...")
            
            # Strategy 3: If still no output, try JavaScript extraction
            if not output_text and not error_text:
                self.logger.debug("Trying JavaScript-based extraction...")
                try:
                    js_output = self.driver.execute_script("""
                        // Try to find any text content in potential output areas
                        var outputs = [];
                        
                        // Look for elements with output-related attributes or classes
                        var candidates = document.querySelectorAll('*[class*="output"], *[id*="output"], *[data-testid*="output"], pre, code');
                        
                        for (var i = 0; i < candidates.length; i++) {
                            var elem = candidates[i];
                            if (elem.offsetParent !== null) {  // Element is visible
                                var text = elem.textContent || elem.innerText || '';
                                if (text.trim().length > 0) {
                                    outputs.push(text.trim());
                                }
                            }
                        }
                        
                        return outputs.slice(-5);  // Return last 5 outputs
                    """)
                    
                    if js_output and isinstance(js_output, list):
                        js_text = '\n'.join([str(item) for item in js_output if str(item).strip()])
                        if js_text.strip():
                            output_text = js_text.strip()
                            self.logger.debug(f"JavaScript extraction found: {output_text[:100]}...")
                            
                except Exception as js_error:
                    self.logger.debug(f"JavaScript extraction failed: {js_error}")
            
            # Final validation and formatting
            output_text = output_text if isinstance(output_text, str) else ""
            error_text = error_text if isinstance(error_text, str) and error_text.strip() else None
            
            # Log results
            if output_text:
                self.logger.info(f"Successfully extracted output ({len(output_text)} chars)")
            if error_text:
                self.logger.info(f"Successfully extracted error ({len(error_text)} chars)")
            if not output_text and not error_text:
                self.logger.warning("No output or error text extracted")
            
            return output_text, error_text
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive output extraction: {e}", exc_info=True)
            return "", f"Output extraction failed: {str(e)}"
    
    def _wait_for_execution_complete(self) -> Tuple[str, Optional[str]]:
        """Legacy method - redirects to improved version."""
        return self._wait_for_execution_complete_with_timeout()

    
    def _extract_cell_output(self) -> Tuple[str, Optional[str]]:
        """Legacy method - redirects to improved safe version."""
        return self._extract_cell_output_safe()
    
    def install_package(self, notebook_id: str, package_name: str) -> Dict[str, Any]:
        """Install a Python package in Colab."""
        try:
            # Ensure notebook is open
            if self.current_notebook_id != notebook_id:
                if not self.open_notebook(notebook_id):
                    raise Exception("Failed to open notebook")
            
            # Create pip install command
            install_code = f"!pip install {package_name}"
            
            # Execute the installation
            result = self.execute_code(notebook_id, install_code)
            
            # Check if installation was successful
            if result.get('success', False):
                # Verify installation by trying to import (for simple packages)
                try:
                    # Try to get package info
                    verify_code = f"import pkg_resources; print(pkg_resources.get_distribution('{package_name.split()[0]}').version)"
                    verify_result = self.execute_code(notebook_id, verify_code)
                    
                    if verify_result.get('success', False) and not verify_result.get('error'):
                        version = verify_result.get('output', '').strip()
                        result['package_version'] = version
                        result['message'] = f"✅ Package '{package_name}' installed successfully (version: {version})"
                    else:
                        result['message'] = f"✅ Package '{package_name}' installation completed"
                        
                except Exception:
                    result['message'] = f"✅ Package '{package_name}' installation completed"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error installing package: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'execution_time': 0,
                'message': f"❌ Failed to install package '{package_name}': {str(e)}"
            }
    
    def upload_file(self, notebook_id: str, file_path: str) -> Dict[str, Any]:
        """Upload a file to Colab environment."""
        try:
            # Ensure notebook is open
            if self.current_notebook_id != notebook_id:
                if not self.open_notebook(notebook_id):
                    raise Exception("Failed to open notebook")
            
            # Get file name
            import os
            file_name = os.path.basename(file_path)
            
            # Create upload code using Colab's files module
            upload_code = f"""
from google.colab import files
import os

# Upload file
uploaded = files.upload()

# Show uploaded files
for filename in uploaded.keys():
    print(f"Uploaded: {{filename}} ({{len(uploaded[filename])}} bytes)")
    
print("Upload completed!")
"""
            
            # Execute the upload code
            result = self.execute_code(notebook_id, upload_code)
            
            if result.get('success', False):
                result['message'] = f"✅ File upload interface opened. Please select and upload '{file_name}'"
                result['file_name'] = file_name
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'execution_time': 0,
                'message': f"❌ Failed to upload file: {str(e)}"
            }
    
    def get_runtime_status(self, notebook_id: str) -> Dict[str, Any]:
        """Get runtime status information."""
        try:
            # Ensure notebook is open
            if self.current_notebook_id != notebook_id:
                if not self.open_notebook(notebook_id):
                    raise Exception("Failed to open notebook")
            
            # Get runtime info using system commands
            info_code = """
import sys
import platform
import psutil
import os

print("=== Runtime Information ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()[0]}")
print(f"Processor: {platform.processor()}")

# Memory info
memory = psutil.virtual_memory()
print(f"Total Memory: {memory.total / (1024**3):.2f} GB")
print(f"Available Memory: {memory.available / (1024**3):.2f} GB")
print(f"Memory Usage: {memory.percent}%")

# Disk info
disk = psutil.disk_usage('/')
print(f"Total Disk: {disk.total / (1024**3):.2f} GB")
print(f"Free Disk: {disk.free / (1024**3):.2f} GB")
print(f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%")

# Check for GPU
try:
    import torch
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        print("GPU: Not available")
except ImportError:
    print("GPU: PyTorch not available")
"""
            return self.execute_code(notebook_id, info_code)
            
        except Exception as e:
            self.logger.error(f"Error getting runtime status: {e}")
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'execution_time': 0,
                'message': f"❌ Failed to get runtime status: {str(e)}"
            }
    
    def close(self) -> None:
        """Close the Selenium manager and cleanup resources."""
        self._close_driver()
        self.current_notebook_id = None
        self.logger.info("Selenium manager closed")
    
    def check_session_health(self) -> bool:
        """Check if the current browser session is healthy and responsive."""
        if not self.driver:
            return False
        
        try:
            # Test basic browser responsiveness
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # Check if we're still on a Colab page
            if "colab.research.google.com" not in current_url:
                self.logger.warning(f"Browser navigated away from Colab: {current_url}")
                return False
            
            # Test basic DOM interaction
            self.driver.find_element(By.TAG_NAME, "body")
            
            self.logger.debug("Browser session health check passed")
            return True
            
        except Exception as e:
            self.logger.warning(f"Browser session health check failed: {e}")
            return False
    
    def cleanup_if_unhealthy(self) -> bool:
        """Cleanup browser session if it's unhealthy. Returns True if cleanup was performed."""
        if not self.check_session_health():
            self.logger.info("Cleaning up unhealthy browser session")
            self._close_driver()
            return True
        return False
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close()