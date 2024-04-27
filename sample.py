import streamlit as st
import zipfile
import os
import shutil
import pandas as pd
import re
from tika import parser


def main():
    st.title("CV's information extractor")
    uploaded_file = st.file_uploader("Upload a zip file", type="zip")

    if uploaded_file is not None:
        name = os.path.splitext(uploaded_file.name)[0]
        data = {'Email': [], 'Contact Number': [], 'Information': []}
        with zipfile.ZipFile(uploaded_file, "r") as infile:
            temp_dir = " "
            os.makedirs(temp_dir, exist_ok=True)
            infile.extractall(temp_dir)

            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    path = os.path.join(root, f)
                    parser_ = parser.from_file(path)
                    content = parser_.get('content')
                    if content:
                        mail = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', re.sub(r'\bE-Mailid-\b', '', content))[0]
                        numbers = re.findall(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b', content)
                        if numbers:
                            num = numbers[0]
                            if num[0]:
                                number = '+' + num[0] + ' ' + num[1] + num[2] + num[3]
                            if not num[0]:
                                number = num[1] + num[2] + num[3]
                        if not numbers:
                            num = re.findall(r'\b(?:\+?(\d{1,3}))?[-. (]*(\d{5})[-. ]*(\d{5})\b', content)[0]
                            if num[0]:
                                number = '+' + num[0] + ' ' + num[1] + num[2]
                            if not num[0]:
                                number = num[1] + num[2]

                        data['Email'].append(mail)
                        data['Contact Number'].append(number)
                        info = re.sub(r'\n\s*\n', '\n\n', content)
                        data['Information'].append(info)

        df = pd.DataFrame(data)
        st.data_editor(df)
        output = f"{name}.xlsx"
        df.to_excel(output, index=False)
        with open(output, "rb") as template_file:
            template_byte = template_file.read()
        st.download_button(label="📥 Download",
                           data=template_byte,
                           file_name=output,
                           mime='application/octet-stream')
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    main()
