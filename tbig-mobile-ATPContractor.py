import unittest
import re
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# Import Appium UiAutomator2 driver for Android platforms (AppiumOptions)
from appium.options.android import UiAutomator2Options
import time

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='0744125184100418',
    appPackage='com.tbig.mobile.develop',
    appActivity='com.tbig.mobile.home.HomeActivity',
    language='en',
    locale='US',
    noReset=True
)

appium_server_url = 'http://localhost:4723'

# Converts capabilities to AppiumOptions instance
capabilities_options = UiAutomator2Options().load_capabilities(capabilities)

class TestAppium(unittest.TestCase):
    def swipe_down(self, duration=500):
        size = self.driver.get_window_size()
        start_y = size['height'] * 0.6  # Mulai dari 80% layar
        end_y = size['height'] * 0.4    # Berakhir di 30% layar
        start_x = size['width'] / 2     # Di tengah horizontal

        self.driver.swipe(start_x, start_y, start_x, end_y, duration)

    def setUp(self) -> None:
        self.driver = webdriver.Remote(command_executor=appium_server_url,options=capabilities_options)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test(self) -> None:
        try:
            section_containers = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.tbig.mobile.develop:id/container']"))
            )
            section_count = len(section_containers)
            print(f"Section count: {section_count}")
            for section_number in range(section_count):
                section_container = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((AppiumBy.ANDROID_UIAUTOMATOR, f"new UiSelector().resourceId(\"com.tbig.mobile.develop:id/container\").instance({section_number})"))
                )

                section_childs = section_container.find_elements(AppiumBy.XPATH, ".//*")
                for section_child_number, section_child in enumerate(section_childs):
                    section_child_resourceID = section_child.get_attribute('resource-id')
                    if section_child_resourceID == "com.tbig.mobile.develop:id/tvTitle":
                        section_title = section_child.text
                    elif section_child_resourceID == "com.tbig.mobile.develop:id/tvStatus":
                        section_status = section_child.text
                        print(f"Section: {section_title}, Status: {section_status}")
                
                    if not section_child.text == "In Progress" and not section_child.text == "Open":
                        continue
                    else:
                        section_container.click()

                        isSectionDone = False
                        temp_previous_photo_title = None
                        previous_photo_title = None
                        previous_photo_number = None

                        while not isSectionDone:
                            vwGroups = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((AppiumBy.CLASS_NAME, "android.view.ViewGroup"))
                            )

                            for vwGroup_number, vwGroup in enumerate(vwGroups):
                                try:
                                    vwGroup_children = vwGroup.find_elements(AppiumBy.XPATH, ".//*")
                                except:
                                    print("Tidak ada ViewGroup ditemukan.")
                                    continue

                                photo_number = None
                                photo_button = None
                                isPhotoTaken = None

                                photo_title = previous_photo_title

                                for vwGroup_child_number, vwGroup_child in enumerate(vwGroup_children):
                                    vwGroup_child_resourceID = vwGroup_child.get_attribute('resource-id')

                                    if vwGroup_child_resourceID == "com.tbig.mobile.develop:id/formElementTitle":
                                        photo_title = vwGroup_child.text
                                        temp_previous_photo_title = photo_title

                                    if vwGroup_child_resourceID == "com.tbig.mobile.develop:id/formElementImagePreview":
                                        isPhotoTaken = True
                                        print(f"{photo_title} | Photo sudah diambil.")
                                    else:
                                        isPhotoTaken = False
                                        if vwGroup_child_resourceID == "com.tbig.mobile.develop:id/containerPlaceholderImagePreview":
                                            print(f"{photo_title} | Photo belum diambil.")

                                    if vwGroup_child_resourceID == "com.tbig.mobile.develop:id/formElementActionCamera":
                                        photo_button = vwGroup_child
                                        print(f"{photo_title} | Button ditemukan.")

                                    if vwGroup_child_resourceID == "com.tbig.mobile.develop:id/formElementError":
                                        print(f"{photo_title} | Flag required ditemukan")
                                        if photo_button:
                                            print(f"{photo_title} | Mengambil photo")
                                            photo_button.click()

                                            photo_capture_button = WebDriverWait(self.driver, 10).until(
                                                EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnCapture"))
                                            )
                                            photo_capture_button.click()

                                            photo_save_button = WebDriverWait(self.driver, 10).until(
                                                EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnSave"))
                                            )
                                            photo_save_button.click()
                                            time.sleep(3)

                                        else:
                                            print("Button belum ditemukan sebelum formElementError.")

                                    if photo_title is not None:
                                        extracted_photo_number = re.search(r'Photo (\d+)', photo_title)
                                        if extracted_photo_number:
                                            previous_photo_number = photo_number
                                            photo_number = int(extracted_photo_number.group(1))  # Cast to int

                                    if photo_number != previous_photo_number:
                                        previous_photo_title = temp_previous_photo_title

                                    if photo_number is not None and photo_number % 15 == 0 and isPhotoTaken:
                                        isSectionDone = True
                                        print("============")
                                        print("Section done")
                                        print("============")

                            self.swipe_down(200)

                        section_complete_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnComplete"))
                        )
                        section_complete_button.click()

                        section_submit_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnSubmit"))
                        )
                        section_submit_button.click()

            task_save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnReviewFinish"))
            )
            task_save_button.click()

            task_finish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnFinish"))
            )
            task_finish_button.click()

            task_submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.tbig.mobile.develop:id/btnActionSecondary"))
            )
            task_submit_button.click()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    unittest.main()