import os
from flask import Flask, request, redirect, render_template, flash,send_file,url_for
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np
# import matplotlib.pyplot as plt
import cv2
import glob
import zipfile


#コピペスタート。
image_size = 28#学習に用いた画像のサイズ
UPLOAD_FOLDER = "warehouse"  #アップロードされた画像を保存するフォルダ名
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) #ALLOWED_EXTENSIONSにはアップロードを許可する拡張子


app = Flask(__name__) 





def allowed_file(filename):#アップロードされたファイルの拡張子のチェックをする関数
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route("/download", methods=["GET"])
def download_api():
    filepath = "./warehouse/test.zip"
    filename = os.path.basename(filepath)
    return send_file(filepath, as_attachment=True,
                     attachment_filename=filename,
                     )




#ここから画像複製の関数を投入。
def scratch_image(img, flip=True, thr=True, blur=True, resize=True, erode=True):
    # ----------------------------ここから書いて下さい----------------------------
    # 水増しの手法を配列にまとめる
    methods = [flip, thr, blur, resize, erode]
    # 画像のサイズを習得、ぼかしに使うフィルターの作成
    img_size = img.shape
    filter1 = np.ones((3, 3))
    # オリジナルの画像データを配列に格納
    images = [img]
    # 手法に用いる関数
    scratch = np.array([
        lambda x: cv2.flip(x, 1),
        lambda x: cv2.threshold(x, 100, 255, cv2.THRESH_TOZERO)[1],
        lambda x: cv2.GaussianBlur(x, (5, 5), 0),
        lambda x: cv2.resize(cv2.resize(
                        x, (img_size[1] // 5, img_size[0] // 5)
                    ),(img_size[1], img_size[0])),
        lambda x: cv2.erode(x, filter1)
    ])
    # 関数と画像を引数に、加工した画像を元と合わせて水増しする関数
    
    doubling_images = lambda f, imag: (imag + [f(i) for i in imag])
    # methodsがTrueの関数で水増し
    for func in scratch[methods]:
        images = doubling_images(func, images)
    
    return images
    # ----------------------------ここまで書いて下さい----------------------------





# @app.route('/')
@app.route("/", methods=['GET', 'POST'])#HTTPメソッドの一種
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
            
            #受け取った画像を読み込む。⇒改造。
            # img = image.load_img(filepath, grayscale=True, target_size=(image_size,image_size))
            img = cv2.imread(filepath)
            result = scratch_image(img)
            for num, im in enumerate(result):
    # まず保存先のディレクトリ"scratch_images/"を指定、番号を付けて保存
                cv2.imwrite("./warehouse/" + str(num) + ".jpg" ,im) 

            
            path = glob.glob("./warehouse/*.jpg")#ifの中。
            with zipfile.ZipFile('./warehouse/test.zip','w') as myzip:
                for image_file in path:
                    myzip.write(image_file)
            return redirect(url_for('download_api'))
        
        # if request.form['send'] == 'aaa':
        #     return render_template('index.html')
        
        # if request.form['send'] == 'bbb':
        #     return render_template('bout.html')
        
        # if request.form['send'] == 'ccc':
        #     return render_template('garelly.html')
        
        
        
        
    return render_template("index.html",answer="")




@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/gallery')
def gallery_page():
    return render_template("gallery.html")



# これが正規。    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ="0.0.0.0",port = port)
    
#コーディング用
# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 8080))
#     app.run("0.0.0.0", debug=True)
    