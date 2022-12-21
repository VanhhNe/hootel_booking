import math
import os
from flask import Blueprint, redirect, render_template, request, session, url_for, send_from_directory, jsonify
from app.db_utils import connect_db, get_cursor
from app.config import HOTEL_IMAGE
from app.sql import *
main_blp = Blueprint(
    "view", __name__, template_folder='templates', static_folder='static')


@main_blp.route('/')
@main_blp.route('/home', methods=['GET'])
def home():
    if session['role_id'] == 0:
        return render_template('admin/admin.html', title='ADMIN PAGE')
    return render_template('home.html')

@main_blp.route('/profile', methods=['GET'])
def profile():
    msg = {}
    id_account = session['id']
    conn = connect_db()
    cursor = get_cursor(conn) 
    try:
        cursor.execute(user['get_account_info']% (id_account,))
        conn.commit()
    except:
        conn.rollback()
    info = cursor.fetchone()
    info = {'account_id': info[0], 'email': info[1], 'user_name': info[2],
            'password': info[3], 'role_id': info[4], 'account_isdelete': info[5]}
    try:
        cursor.execute(user['get_customer_info']% (id_account, ))
        conn.commit()
    except:
        conn.rollback()
    khachhang = cursor.fetchone()

    if khachhang:
        khachhang = {'customer_id': khachhang[0], 'first_name': khachhang[1], 'last_name': khachhang[2], 'account_id': khachhang[3], 'customer_identity': khachhang[4], 'customer_gender': khachhang[5],
                 'customer_phone': khachhang[6], 'customer_address': khachhang[7], 'customer_date': khachhang[8], 'customer_note': khachhang[10], 'customer_nation': khachhang[9]}
    conn.close()
    return render_template('user/profile.html', info=info,khachhang=khachhang,msg=msg)

@main_blp.route('/rooms/pages/<id_filter>/<page>', defaults={'page': 1, 'id_filter': 'price_down'})
@main_blp.route('/rooms/pages/<id_filter>/{int:page}', methods=['GET', 'POST'])
def room(page,id_filter):

    limit = 5
    offset = page * limit - limit
    conn = connect_db()
    cursor = get_cursor(conn)
    try:
        cursor.execute('SELECT * FROM phong')
        conn.commit()
    except:
        conn.rollback()
    total_row = cursor.rowcount
    total_page = math.ceil(total_row/limit)

    next = page + 1
    prev = page - 1
    try:
        cursor.execute('SELECT * FROM phong')
        conn.commit()
    except:
        conn.rollback()
    total_row = cursor.rowcount
    total_page = math.ceil(total_row/limit)
    
    if (id_filter == 'price_down'):
        try:
            cursor.execute(
                'SELECT * FROM phong ORDER BY room_price DESC LIMIT %s OFFSET %s', (limit, offset,) )
            conn.commit()
        except:
            conn.rollback()
    elif (id_filter == 'price_up'):
        try:
            cursor.execute(
                'SELECT * FROM `phong` ORDER BY `phong`.`room_price` DESC LIMIT %s OFFSET %s', (limit, offset,))
            conn.commit()
        except:
            conn.rollback()
    elif (id_filter == 'rating'):
        try:
            cursor.execute(
                'SELECT * FROM phong ORDER BY room_price DESC LIMIT %s OFFSET %s', (limit, offset,))
            conn.commit()
        except:
            conn.rollback()
    elif (id_filter == 'most_popular'):
        try:
            cursor.execute(
                'SELECT * FROM phong ORDER BY room_price DESC LIMIT %s OFFSET %s', (limit, offset,))
            conn.commit()
        except:
            conn.rollback()
    else:
        try:
            cursor.execute(
                'SELECT * FROM phong ORDER BY room_id DESC LIMIT %s OFFSET %s', (limit, offset,))
            conn.commit()
        except:
            conn.rollback()
    datas = cursor.fetchall()
    final_data = []
    for data in datas:
        temp_data = {'room_id': data[0], 'room_name': data[1], 'room_address': data[2],
                     'room_performance': data[3], 'room_price': data[4], 'id_typeroom': data[5], 'room_isdelete': data[6]}
        room_id = int(data[0])
        try:
            cursor.execute(
                'SELECT image_link, image_rank from hinhanh where room_id = % s;', (room_id,))
            conn.commit()
        except:
            conn.rollback()
        img = cursor.fetchone()
        index = img[0].index('/')
        img = {'folder': img[0][0:index],
               'name': img[0][index+1:], 'rank': img[1]}
        final_data.append((temp_data, img))
    conn.close()
    return render_template('room.html', data=final_data, page=total_page, next=next, prev=prev, id_filter=id_filter)


@main_blp.route('/detail/<room_id>', methods=['GET', 'POST'])
def detail(room_id):
    msg = ''
    conn = connect_db()
    cursor = get_cursor(conn)
    try:
        cursor.execute(
            'SELECT * FROM phong where room_id = %s', (room_id,))
        conn.commit()
    except:
        conn.rollback()
    data = cursor.fetchone()

    data = {'room_id': data[0], 'room_name': data[1], 'room_address': data[2],
                    'room_performance': data[3], 'room_price': data[4], 'id_typeroom': data[5], 'room_isdelete': data[6]}
    try:
        cursor.execute(
            'SELECT image_link, image_rank from hinhanh where room_id = % s;', (room_id,))
        conn.commit()
    except:
        conn.rollback()
    imgs = cursor.fetchall()
    list_img = []
    for img in imgs:

        index = img[0].index('/')
        img = {'folder': img[0][0:index],
            'name': img[0][index+1:], 'rank': img[1]}
        list_img.append(img)
    conn.close()
    return render_template('detail.html', data=data, msg=msg, img=list_img)


@main_blp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET' and 'province' in request.form:
        province = request.form('province')
        conn = connect_db()
        cursor = get_cursor(conn)
        try:
            cursor.execute('select phong.room_id, phong.room_name, phong.room_address, phong.room_performence, phong.room_price, phong.id_roomtype * from phong inner join tinhthanh on tinhthanh.province_id = phong.id_province where tinhthanh.province_name = %s;', (province,))
            conn.commit()
        except:
            conn.rollback()
        datas = cursor.fetchall()
        final_data = []
        for data in datas:
            temp_data = {'room_id': data[0], 'room_name': data[1], 'room_address': data[2],
                         'room_performance': data[3], 'room_price': data[4], 'id_typeroom': data[5], 'room_isdelete': data[6]}
            room_id = int(data[0])
            try:
                cursor.execute(
                    'SELECT image_link, image_rank from hinhanh where room_id = % s;', (room_id,))
                conn.commit()
            except:
                conn.rollback()
            img = cursor.fetchone()
            index = img[0].index('/')
            img = {'folder': img[0][0:index],
                   'name': img[0][index+1:], 'rank': img[1]}
            final_data.append((temp_data, img))
    return render_template('room.html', data=final_data)

@main_blp.route('/fetchrecords', methods=['POST', 'GET'])
def fetchrecords():
    if request.form == "POST":
        query = request.form['action']
        minimum_price = request.form['minimum_price']
        maximum_price = request.form['maximum_price']
        print(minimum_price)
        print(maximum_price)
    return render_template('filter.html')
@main_blp.route('/folder_image/<folder>/<name>')
def image_file(folder, name):
    return send_from_directory(os.path.join(HOTEL_IMAGE, folder), name)
