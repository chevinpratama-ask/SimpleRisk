from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from SimpleRisk_FAD1_SuretyBond import test_tc_01
from SimpleRisk_FAD1_KontraBankGaransi import test_TC_02


def test_all():
    # Jalankan test_tc_01
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    test_tc_01(driver)
    driver.quit()

    # Jalankan test_TC_02
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    test_TC_02(driver)
    driver.quit()