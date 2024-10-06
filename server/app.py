from flask import Flask, render_template, request, jsonify, redirect, url_for
import openai
import os
import requests
    
# OpenAI API anahtarını ayarla
openai.api_key = "sk-6qcxsNFps32b65Mk30Rozfg_Q_oCyTArWbd-VpY6VgT3BlbkFJmeOVl2IctpXAfskxdZewTqp_rPNFoIJPxGFt1ieLkA"

app = Flask(__name__)

hisList = list()
history = ""
future = ""
counter = 0
# Function to send a POST request to the model using ChatCompletion
def get_ai_response(user_input):
    print(user_input)
    global history
    global counter
    
    if user_input == "reset":
        history = ""
        return None
    
    counter += 1
    history += f"{counter}. prompt: "+ user_input
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"Write a story about a young boy named {user_input} who experiences a daily negative event in the park due to greenhouse gases. At the story's most critical moment, present three alternative choices. Progress the story based on these choices, pausing at critical moments to present three choices each time, repeating this process three times in total. Every time choices are presented, let us know what they are and wait for our response. Continue the story based on our responses."},
                {"role": "user", "content":"You said that, " + history + " " + "We choosed, " + user_input}
            ]
        )
        # Yanıtı al
        result = completion.choices[0].message['content']
        history += f"{counter}. answer: " + result
        completion2 = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
        {"role": "system", "content": "Convert a key moment from the entered story into a detailed, visual prompt for DALL-E, ensuring the prompt does not exceed 175 words.Do not surp us 175 word limit."},
        {
            "role": "user",
            "content": result
        }
            ]
            )
        textDal = completion2.choices[0].message.content

        response = openai.Image.create(
        model="dall-e-2",
        prompt= textDal,
        size="256x256",
        quality="standard",
        n=1,
        )
        image_url = response.data[0].url
        response = requests.get(image_url)
        if response.status_code == 200:
            with open("./server/static/assets/ahmet.png", "wb") as file:
                file.write(response.content)
            print("Görsel başarıyla kaydedildi.")
        else:
            print("Görsel indirilemedi.")
        index = result.find("Critical Moment")

        # Insert a newline character before "Critical Moment"
        if index != -1:
            updated_text = result[:index] + "\n\n" + text[index:]
            print(updated_text)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Ana sayfa route'u
@app.route('/')
def index():
    return render_template('index.html')

# 1. Sayfanın route'u
@app.route('/category1')
def category1():
    return render_template('1.html')

# Tables route'u
@app.route('/tables')
def tables():
    return render_template('tables.html')

# İletişim sayfası route'u
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    result = request.args.get('result', "")  # İlk başta boş bir değer ayarlıyoruz
    if not result:  # Eğer result gerçekten boşsa hiçbir metin gösterilmesin
        result = ""
    return render_template('generate-a-climate-story.html', result=result)

@app.route('/postdata', methods=['POST'])
def postdata():
    if request.method == 'POST':
        user_input = request.form['user_input']
        result = get_ai_response(user_input)
        # result'ı URL parametresi olarak geçiriyoruz
        return redirect(url_for('generate', result=result))

@app.route('/postmapdata', methods=['GET','POST'])
def postmapdata():
    

    cat = request.form.get('category')
    date1 = request.form.get('first_option')
    date2 = request.form.get('last_option')
    
    print(cat,",", date1,",",date2)
    with open("./server/maps/datas.txt", "w") as dosya:
        dosya.write(f"{cat},{date1},{date2}")
        
    os.system(f'python ./server/maps/{str(cat)}.py')



    return render_template('maps.html')

@app.route('/posttabledata', methods=['GET', 'POST'])
def posttabledata():
    
    table_cat = request.form.get('table_category')
    table_user_input = request.form.get('table_user_input')
    
    print(table_user_input, ",", table_cat)
    with open("./server/tables/datas.txt", "w", encoding="utf-8") as dosya:
        dosya.write(f"{table_user_input},{table_cat}")
    
    os.system(f'python ./server/tables/{str(table_cat)}t.py')
    
    return render_template('tables_result.html')
               

# Ekibimiz sayfası
@app.route('/ourteam')
def ourteam():
    return render_template('ourteam.html')

# Mapping sayfası
@app.route('/mapping')
def mapping():
    return render_template('mapping.html')

# Flask uygulamasını başlatma
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
