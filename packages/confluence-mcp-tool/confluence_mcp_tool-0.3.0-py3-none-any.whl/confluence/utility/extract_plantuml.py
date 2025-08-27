"""Extract and decode PlantUML diagrams from Confluence macro XML content."""

import base64
import os
import re
import zlib


def extract_filename_without_extension(xml_content):
    """Extract the filename parameter from Confluence XML and remove the .svg extension.

    Args:
        xml_content (str): The Confluence XML containing structured macro data

    Returns:
        str: Filename without the .svg extension or None if not found
    """
    # Look for the filename parameter using regex
    pattern = r'<ac:parameter ac:name="filename">(.*?)</ac:parameter>'
    filename_match = re.search(pattern, xml_content, re.DOTALL)

    if filename_match:
        # Extract the filename
        filename = filename_match.group(1)

        # Remove any file extension
        base_name, _ = os.path.splitext(filename)
        return f"{base_name}.puml"

    return None


def decode_plantuml(encoded_data):
    """Decode PlantUML compressed data from Confluence macro.

    This function attempts to decompress PlantUML data that has been encoded
    using PlantUML's compression algorithm.

    Args:
        encoded_data (str): The encoded PlantUML string

    Returns:
        str: Decoded PlantUML text or None if decompression fails
    """
    # For compressed data, attempt decompression using zlib with negative window bits
    # (negative window bits indicates raw deflate data with no header/footer)
    try:
        inflated = zlib.decompress(base64.b64decode(encoded_data), -zlib.MAX_WBITS)
        return inflated.decode("utf-8")
    except Exception as e:
        print(f"Decompression failed: {e}")

    return None


def extract_plantuml_from_confluence_macro(xml_content):
    """Extract PlantUML data from Confluence macro XML."""
    pattern = r'<ac:parameter\s+ac:name="data">(.*?)</ac:parameter>'
    match = re.search(pattern, xml_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_and_decode_plantuml_from_confluence_macro(xml_content):
    """Extract and decode PlantUML data from Confluence macro XML."""
    compressed_data = extract_plantuml_from_confluence_macro(xml_content)
    if not compressed_data:
        print("Failed to extract PlantUML data from the XML")
        return None

    # Decode the PlantUML data
    plantuml_code = decode_plantuml(compressed_data)

    if plantuml_code:
        # print("Decoded PlantUML code:")

        # Check if the result is URL-encoded
        if "%40startuml" in plantuml_code:
            import urllib.parse

            plantuml_code = urllib.parse.unquote(plantuml_code)
            # print("Detected URL encoding, decoded it")

        # print(plantuml_code)
    else:
        print("Failed to decode the PlantUML data")

    filename = extract_filename_without_extension(xml_content)

    return plantuml_code, filename


if __name__ == "__main__":
    # Replace this with your actual XML content or load from a file
    CONFLUENCE_XML = """<ac:structured-macro ac:name=\"plantumlcloud\" ac:schema-version=\"1\"
        data-layout=\"full-width\" ac:local-id=\"cfef55a8-f6a3-453c-955d-3fc2f545cca6\"
        ac:macro-id=\"172d1cdf-9fb8-4876-8cd3-29e0675384f3\">
        <ac:parameter ac:name=\"toolbar\">bottom</ac:parameter>
        <ac:parameter ac:name=\"filename\">frontend.svg</ac:parameter>
        <ac:parameter ac:name=\"originalHeight\">384</ac:parameter>
        <ac:parameter ac:name=\"data\">
            pVVdb9owFP01UdeHVlnohvoYAkxItIpge9lLZGInWCR26jhl3a/fvb75AlVjK5EFju/HOT732vEe/NoyY5uy8PwQxo0X+HtrK28SesESRlUwheb7VJfwGuPrj6d1smYqb1guko3IhBEqFcm3RnJxX/GMUllpCwHppHpppHmLtKm0YVasNVORLitmxEpl2pTMSq0Q+3+fli8XmVSIxCXLDQOaPiS3MpUVkK0/mBkGS602kG0jXhpR49wt73SjODNvYPGCYB1vYTJbglgBTFgNP7ss84LJ12k0XQRdzC9y/wkaFDCNjU5FXVMQOM+WiwBynGc/cXO5j9ocskIfKazHEIojMMA4vCvkpJJYqXJ40RUW56Ma7qEhXEZte2Y3rLFaNeVOtHLWB6mgXq5uUErWFHaplX1mJcZCp8gU/rdM4e6ftmcRNdYGug/lmM7AGA+ln2nDhYl04aq4K1h6OHOAldyg4J0TSBo+zqP58tTxAqEzz638jZ6fv4ApxB76Ow65vMs1NEYfL4B70/l1BeeiTo3ciVM1NbSwL17FVSdoODmBf+dNFu3ZwMvFBwt1+XT2j1dE4H+6pdgLnhtRV9C1gqSBYyxfwbcFd8SwGhUsrAh5nBLmhmjjXSiR/RsGYdHoZHdbGR9FosUKPNvuSkW2IwdFBfQmc0R9/p5E8TopgH2SEv1EDvyTVpDbHne0hzFqZ+7W7kYid6Q6Wy9KF8TFe1np+iDQAnchMRVTqFEYr7ApFK+0VGgT0J+m96ehNGko873t+qjlc+pIY88Md5ppqEfkxLeNUSSjbWr48PBBuUd4ztLQzedQOwMt9bciFZvuYapfK9PQnk6pHtkMUp2INGwDxgPCwJfxDw==
        </ac:parameter>
        <ac:parameter ac:name=\"compressed\">true</ac:parameter>
        <ac:parameter ac:name=\"originalWidth\">1200</ac:parameter>
        <ac:parameter ac:name=\"revision\">3</ac:parameter>
    </ac:structured-macro>"""

    plant_uml = extract_and_decode_plantuml_from_confluence_macro(CONFLUENCE_XML)
    if plant_uml:
        plantuml_code, filename = plant_uml
        # Optionally save to a file
        if plantuml_code:
            with open("output/frontend_diagram.puml", "w") as f:
                f.write(plantuml_code)
            print("\nSaved to frontend_diagram.puml")
