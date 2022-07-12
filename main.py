import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np

# 分類したいクラス名をclassesリストに格納
classes = ["0","1","2","3","4","5","6","7","8","9"]
image_size = 28#学習に用いた画像のサイズ

UPLOAD_FOLDER = "uploads"  #アップロードされた画像を保存するフォルダ名
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) #ALLOWED_EXTENSIONSにはアップロードを許可する拡張子

app = Flask(__name__)      #Flaskクラスのインスタンスを作成

def allowed_file(filename):#アップロードされたファイルの拡張子のチェックをする関数
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = load_model('./model.h5')#学習済みモデルをロード


@app.route('/', methods=['GET', 'POST'])#HTTPメソッドの一種
def upload_file():
    if request.method == 'POST':#ウェブ上のフォームから送信したデータを扱うための関数
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)#引数に与えられたurlに移動する関数
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            #受け取った画像を読み込み、np形式に変換
            img = image.load_img(filepath, grayscale=True, target_size=(image_size,image_size))
            img = image.img_to_array(img)
            data = np.array([img])
            #変換したデータをモデルに渡して予測する
            result = model.predict(data)[0]
            predicted = result.argmax()
            pred_answer = "これは " + classes[predicted] + " です"

            return render_template("index.html",answer=pred_answer)

    return render_template("index.html",answer="")


if __name__ == "__main__":                   #Herokuへデプロイし、全世界に公開
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)