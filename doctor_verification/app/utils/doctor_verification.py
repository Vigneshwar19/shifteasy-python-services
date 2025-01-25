from flask import jsonify
from playwright.sync_api import sync_playwright
from app.utils.data_format import format_data

def doctor_verification(url, reg_no, council, customerId):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            page.click('a[data-toggle="tab"][href="#registrationNumber"]')

            page.wait_for_selector('#doct_regdNo', timeout=5000)

            page.fill('#doct_regdNo', reg_no)

            page.click('#doctor_regdno_details')

            page.wait_for_selector('select[name="doct_info3_length"]', timeout=5000)
            page.select_option('select[name="doct_info3_length"]', value="10")

            page.wait_for_selector('#doct_info3', timeout=5000)

            headers = page.query_selector_all('#doct_info3 th')
            state_medical_council_index = None
            for index, header in enumerate(headers):
                if "State Medical Councils" in header.text_content():
                    state_medical_council_index = index
                    break

            if state_medical_council_index is None:
                return jsonify({"error": "State Medical Councils column not found"}), 400

            table_data = []
            rows = page.query_selector_all('#doct_info3 tr')
            matching_row = None
            for row in rows:
                cells = row.query_selector_all('td')
                row_data = [cell.text_content().strip() for cell in cells]
                if row_data and len(row_data) > state_medical_council_index:
                    if row_data[state_medical_council_index] == council and reg_no in row_data:
                        matching_row = row
                        table_data.append(row_data)

            if matching_row:
                view_link = matching_row.query_selector('a[onclick*="openDoctorDetailsnew"]')
                view_link.click()

                page.wait_for_selector('#doctorModalBody', timeout=5000)
                page.wait_for_selector('#doctorBiodata', timeout=5000)

                modal_headers = page.query_selector_all('#doctorBiodata th')
                modal_header_data = [header.text_content().strip() for header in modal_headers]

                modal_table_data = []
                modal_rows = page.query_selector_all('#doctorBiodata tr')
                for modal_row in modal_rows:
                    modal_cells = modal_row.query_selector_all('td')
                    modal_row_data = [cell.text_content().strip() for cell in modal_cells]
                    if modal_row_data:
                        modal_table_data.append(modal_row_data)

                browser.close()

                formatted_response = format_data({
                    "message": "Matching record found and modal data extracted",
                    "customerId": customerId,
                    "table_data": table_data,
                    "modal_data": {
                        "headers": modal_header_data,
                        "data": modal_table_data
                    }
                })

                return formatted_response, 200
            else:
                browser.close()
                return jsonify({"message": "No matching records found"}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500