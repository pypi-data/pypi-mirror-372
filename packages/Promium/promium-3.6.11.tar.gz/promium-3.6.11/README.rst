Promium
=======

.. image:: https://img.shields.io/badge/Python%3A%203.13-blue
   :target: https://pypi.org/project/Promium/

.. image:: https://badge.fury.io/py/Promium.svg
   :target: https://badge.fury.io/py/Promium

Promium is a simple Selenium wrapper designed to facilitate writing UI tests.

`Promium Documentation <https://qa-automation.git-doc.evo.dev/promium>`_

Overview
--------

Promium simplifies the UI testing process using Selenium. The framework is designed for ease of test creation and provides essential tools for working with elements, pages, and test cases. Supports Python 3.13 and works on Linux and macOS.

Installation and Setup
----------------------

**System Requirements**

- Python 3.13
- Systems: Linux, macOS

To install all dependencies:

.. code-block:: text

   pip install -r requirements.txt

**Install Promium**

.. code-block:: text

   pip install promium

**Driver and Chrome Setup**

To use Promium with Chrome, both Google Chrome and ChromeDriver need to be installed. Use the following commands to set up Chrome and ChromeDriver:

.. code-block:: text

   ARG CHROME_MILESTONE=130

   #============================================
   # Google Chrome
   #============================================
   RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MILESTONE}) && \
       curl -Lo /tmp/chrome-linux.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
       apt-get install -y unzip && \
       unzip /tmp/chrome-linux.zip -d /usr/local/ && \
       ln -s /usr/local/chrome-linux64/chrome /usr/local/bin/google-chrome && \
       rm /tmp/chrome-linux.zip

   #============================================
   # ChromeDriver
   #============================================
   RUN CHROME_DRIVER_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json | python3 -c "import sys, json; print(json.load(sys.stdin)['milestones'][str(${CHROME_MILESTONE})]['version'])") && \
       wget --no-verbose -O /tmp/chromedriver_linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
       unzip /tmp/chromedriver_linux64.zip -d /opt/selenium && \
       ln -fs /opt/selenium/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
       rm /tmp/chromedriver_linux64.zip

Usage Examples
--------------

Below is a basic example of how to define a page object and run a simple test. For more examples, refer to the `Examples Documentation <https://github.com/your-repo-path/promium/doc/examples.md>`_.

**Page Object Example**

.. code-block:: text

    from selenium.webdriver.common.by import By
    from promium import Page, Block, Element, InputField, Link

    class ResultBlock(Block):
        title = Link(By.CSS_SELECTOR, 'h3')
        link = Element(By.CSS_SELECTOR, '.f')
        description = Element(By.CSS_SELECTOR, '.st')
        tags = Element.as_list(By.CSS_SELECTOR, '.osl .fl')

    class GoogleResultPage(Page):
        results_blocks = ResultBlock.as_list(By.CSS_SELECTOR, '#rso .srg div.g')

    class GoogleMainPage(Page):
        url = 'https://google.com'
        logo = Element(By.CSS_SELECTOR, '#hplogo')
        search_input = InputField(By.CSS_SELECTOR, '[name="q"]')

        def search(self, text):
            self.search_input.send_keys(text)
            self.search_input.submit()
            return GoogleResultPage(self.driver)


**Test Example**

.. code-block:: text

    from promium.test_case import WebDriverTestCase
    from tests.pages.google_page import GoogleMainPage

    class TestMainGooglePage(WebDriverTestCase):
        def test_search(self):
            main_page = GoogleMainPage(self.driver)
            main_page.open()
            self.soft_assert_element_is_displayed(main_page.logo)
            result_page = main_page.search('Selenium')
            result_block = result_page.results_blocks.first_item
            self.soft_assert_in('Selenium', result_block.title.text)


**Run a Simple Test**

.. code-block:: text

   # all tests
   pytest tests/

   # all tests in suite
   pytest tests/test_google.py

   # only one test
   pytest tests/test_google.py -k test_search

Development and Testing
-----------------------

To set up a development environment and run tests, use the following commands:

- **Build Docker Image**: `docker build -t promium/base-env .`
- **Run Tests**: `docker-compose run test-se`
- **Check Linting**: `docker-compose run ruff`

Additional Documentation
------------------------

For detailed information on using and configuring Promium, refer to the following documentation files:


- `Assertions <./doc/assertions.md>`_ - Description of available assertion methods for validating test conditions.
- `CI Setup <./doc/ci.md>`_ - Configuration of CI/CD for automating integration processes.
- `Commands <./doc/command.md>`_ - List of available commands and their usage within the framework.
- `Containers <./doc/containers.md>`_ - Information on setting up and using containers for an isolated testing environment.
- `Devices(emulation) <./doc/device.md>`_ - Description of supported devices and configurations.
- `Drivers <./doc/driver.md>`_ - Configuration of drivers for browser interaction.
- `Elements <./doc/element.md>`_ - Working with web elements and their properties.
- `Examples <./doc/examples.md>`_ - Sample tests and scenarios to get started with the framework.
- `Exceptions <./doc/exceptions.md>`_ - Handling exceptions and errors during testing.
- `Test Cases <./doc/test_case.md>`_ - Creating and structuring test cases in Promium.



