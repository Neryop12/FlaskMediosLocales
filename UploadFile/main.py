import os
#import magic
import urllib.request
from app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import numpy as mp
import mysql.connector as mysql
ALLOWED_EXTENSIONS = set(['xls', 'xlsx'])

conn = None
def openConnection():
    global conn
    try:
        conn = mysql.connect(host='34.201.99.133', database='MediaPlatforms',
                             user='omgdev', password='Sdev@2002!', autocommit=True)
    except:
        print("ERROR: NO SE PUEDO ESTABLECER CONEXION MYSQL.")
        sys.exit()


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')


def ProcessFile(conn,file):
    #querys
    sql_insert_blob_query = """ INSERT INTO localmedia (Medio, Cliente,Pais, Campana, Nomenclatura, StartDate, EndDate, Mes, ODC,AccountID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    #Formato de las fechas para aceptar en el GET
    sql_select_account = "select AccountsID from Accounts where Account = %s and Country = %s;"
    sql_last = "SELECT LAST_INSERT_ID();"
    sql_insert_det = "Insert INTO detaillocalmedia (LocalMediaID, StartWeek, EndWeek, Nomenclatura, Formato, Objetivo, Impresiones, Clicks, CTR, Consumo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    print (datetime.now())
    cur=conn.cursor(buffered=True)
    campanas=[]
    try:
        file = file
        df = pd.read_excel(file,index_col=0)
        df = df.to_numpy()
        Medio =  df[0][1]
        Cliente =  df[1][1]
        Pais  =  df[2][1]
        Campana =  df[3][1]
        Nomenclatura =  df[4][1]
        FechaInicio =  (df[5][1]).strftime("%Y-%m-%d")
        FechaFin =   (df[6][1]).strftime("%Y-%m-%d")
        Mes =  df[7][1]
        Odc =  df[8][1]
        #cur.execute(sql_select_account, (str(df[0][1]),str(df[2][1])))
        #rescampaing = cur.fetchone()
        #if rescampaing is not None:
        cur.execute(sql_insert_blob_query,(Medio, Cliente, Pais, Campana, Nomenclatura, FechaInicio, FechaFin, Mes, Odc, 135373))
        cur.execute(sql_last)
        lastID = cur.fetchone()
        for row in df[11:]:
            StartWeek =  (row[0]).strftime("%Y-%m-%d")
            EndWeek =   (row[1]).strftime("%Y-%m-%d")
            Impresiones = row[5]
            Clicks = row[6]
            #Impresiones = row[7] Falta el nan, cuando viene nullo                
            cur.execute(sql_insert_det,(lastID[0],StartWeek,EndWeek,row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
            
            
    except Exception as e:
        print(e)
    finally:
        pass
    


@app.route('/', methods=["GET",'POST'])
def upload_file():
    if request.method == 'POST':
        cliente = request.form['cliente']
        medio = request.form['medio']
        pais = request.form['pais']
        if 'file' not in request.files:
            flash('No File part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            name = file.filename.split('.')
            filename = secure_filename(name[0] +  str(datetime.now()) + '.' +name[1])
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            ProcessFile(conn, file)
            flash('file successfull uploaded')
            return redirect('/')
        else:
            flash('Allowed file type are xls, xlsx')
            return redirect(request.url)







if __name__ == "__main__":
    openConnection()
    app.run(debug=False)
    conn.close()