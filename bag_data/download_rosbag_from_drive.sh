#!/bin/bash

# フォルダIDを指定
FOLDER_ID="1z7xKH1WpxLZ8B4Gqx2nPy_awg_xzuiTR"

# gdownを使ってフォルダをダウンロード
gdown --folder https://drive.google.com/drive/folders/$FOLDER_ID -O .

echo "Download completed. Files are saved in ./downloaded_files directory."
