"""Diagnostic tools for troubleshooting WebDriver and Colab issues."""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .colab_selenium import ColabSeleniumManager


class ColabDiagnostics:
    """Diagnostic tools for Colab WebDriver issues."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize diagnostics."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics."""
        results = {
            "timestamp": time.time(),
            "webdriver_test": self._test_webdriver_creation(),
            "colab_access_test": self._test_colab_access(),
            "element_detection_test": self._test_element_detection(),
            "recommendations": []
        }
        
        # Generate recommendations based on results
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _test_webdriver_creation(self) -> Dict[str, Any]:
        """Test WebDriver creation with different configurations."""
        results = {
            "chrome_regular": False,
            "chrome_headless": False,
            "chrome_undetected": False,
            "firefox": False,
            "errors": []
        }
        
        # Test regular Chrome
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            driver.quit()
            results["chrome_regular"] = True
        except Exception as e:
            results["errors"].append(f"Chrome regular: {str(e)}")
        
        # Test headless Chrome
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            driver.quit()
            results["chrome_headless"] = True
        except Exception as e:
            results["errors"].append(f"Chrome headless: {str(e)}")
        
        # Test undetected Chrome
        try:
            import undetected_chromedriver as uc
            driver = uc.Chrome()
            driver.quit()
            results["chrome_undetected"] = True
        except Exception as e:
            results["errors"].append(f"Chrome undetected: {str(e)}")
        
        # Test Firefox
        try:
            options = webdriver.FirefoxOptions()
            driver = webdriver.Firefox(options=options)
            driver.quit()
            results["firefox"] = True
        except Exception as e:
            results["errors"].append(f"Firefox: {str(e)}")
        
        return results
    
    def _test_colab_access(self) -> Dict[str, Any]:
        """Test access to Google Colab."""
        results = {
            "can_reach_colab": False,
            "page_loads": False,
            "requires_auth": False,
            "interface_detected": False,
            "errors": []
        }
        
        driver = None
        try:
            # Create a simple driver for testing
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            
            # Try to access Colab
            driver.get("https://colab.research.google.com")
            results["can_reach_colab"] = True
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            results["page_loads"] = True
            
            # Check if authentication is required
            if "accounts.google.com" in driver.current_url:
                results["requires_auth"] = True
            
            # Try to detect Colab interface elements
            interface_selectors = [
                "colab-notebook-container",
                "[data-testid='notebook-container']",
                ".notebook-container",
                "colab-notebook"
            ]
            
            for selector in interface_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        results["interface_detected"] = True
                        break
                except Exception:
                    continue
            
        except Exception as e:
            results["errors"].append(str(e))
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        return results
    
    def _test_element_detection(self) -> Dict[str, Any]:
        """Test detection of Colab interface elements."""
        results = {
            "selectors_found": [],
            "selectors_failed": [],
            "total_elements": 0
        }
        
        # All selectors we use in the main code
        test_selectors = [
            # Interface selectors
            "colab-notebook-container",
            "[data-testid='notebook-container']",
            ".notebook-container",
            # Cell selectors
            "colab-cell[cell-type='code']",
            "[data-testid='code-cell']",
            ".code-cell",
            # Button selectors
            "colab-add-cell-button",
            "button[data-testid='add-code-cell']",
            # Output selectors
            "colab-output-area",
            "[data-testid='cell-output']",
            ".cell-output"
        ]
        
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=options)
            
            # Go to a sample Colab notebook (if possible)
            driver.get("https://colab.research.google.com")
            time.sleep(3)
            
            for selector in test_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        results["selectors_found"].append({
                            "selector": selector,
                            "count": len(elements)
                        })
                        results["total_elements"] += len(elements)
                    else:
                        results["selectors_failed"].append(selector)
                except Exception as e:
                    results["selectors_failed"].append(f"{selector}: {str(e)}")
            
        except Exception as e:
            results["error"] = str(e)
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        
        return results
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on diagnostic results."""
        recommendations = []
        
        webdriver_results = results.get("webdriver_test", {})
        colab_results = results.get("colab_access_test", {})
        element_results = results.get("element_detection_test", {})
        
        # WebDriver recommendations
        if not any([webdriver_results.get("chrome_regular"), 
                   webdriver_results.get("chrome_headless"),
                   webdriver_results.get("firefox")]):
            recommendations.append("❌ No WebDriver working - install ChromeDriver or GeckoDriver")
        elif webdriver_results.get("chrome_undetected"):
            recommendations.append("✅ Use undetected-chromedriver for better stealth")
        elif webdriver_results.get("chrome_regular"):
            recommendations.append("⚠️ Regular Chrome works but may be detected - consider stealth measures")
        
        # Colab access recommendations
        if not colab_results.get("can_reach_colab"):
            recommendations.append("❌ Cannot reach Colab - check internet connection")
        elif colab_results.get("requires_auth"):
            recommendations.append("🔐 Authentication required - ensure Google credentials are set up")
        elif not colab_results.get("interface_detected"):
            recommendations.append("⚠️ Colab interface not detected - selectors may need updating")
        
        # Element detection recommendations
        if element_results.get("total_elements", 0) == 0:
            recommendations.append("❌ No Colab elements detected - major selector update needed")
        elif len(element_results.get("selectors_failed", [])) > len(element_results.get("selectors_found", [])):
            recommendations.append("⚠️ Many selectors failing - partial selector update needed")
        
        if not recommendations:
            recommendations.append("✅ All diagnostics passed - WebDriver should work correctly")
        
        return recommendations
    
    def save_diagnostics_report(self, results: Dict[str, Any], filepath: str) -> None:
        """Save diagnostics results to a file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            self.logger.info(f"Diagnostics report saved to: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save diagnostics report: {e}")


def run_diagnostics_cli():
    """CLI entry point for running diagnostics."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Run Colab WebDriver diagnostics")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--output", help="Output file for results")
    args = parser.parse_args()
    
    # Load config
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Run diagnostics
    diagnostics = ColabDiagnostics(config)
    results = diagnostics.run_full_diagnostics()
    
    # Print results
    print("🔍 Colab WebDriver Diagnostics Results")
    print("=" * 50)
    
    print("\n📊 WebDriver Tests:")
    webdriver_results = results["webdriver_test"]
    for test, passed in webdriver_results.items():
        if test != "errors":
            status = "✅" if passed else "❌"
            print(f"  {status} {test}: {passed}")
    
    if webdriver_results.get("errors"):
        print("\n❌ WebDriver Errors:")
        for error in webdriver_results["errors"]:
            print(f"  - {error}")
    
    print("\n🌐 Colab Access Tests:")
    colab_results = results["colab_access_test"]
    for test, result in colab_results.items():
        if test != "errors":
            status = "✅" if result else "❌"
            print(f"  {status} {test}: {result}")
    
    if colab_results.get("errors"):
        print("\n❌ Colab Access Errors:")
        for error in colab_results["errors"]:
            print(f"  - {error}")
    
    print("\n🎯 Element Detection:")
    element_results = results["element_detection_test"]
    print(f"  Total elements found: {element_results.get('total_elements', 0)}")
    print(f"  Selectors working: {len(element_results.get('selectors_found', []))}")
    print(f"  Selectors failing: {len(element_results.get('selectors_failed', []))}")
    
    print("\n💡 Recommendations:")
    for rec in results["recommendations"]:
        print(f"  {rec}")
    
    # Save to file if requested
    if args.output:
        diagnostics.save_diagnostics_report(results, args.output)
        print(f"\n📄 Full report saved to: {args.output}")


if __name__ == "__main__":
    run_diagnostics_cli()