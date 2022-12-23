import re
from flask import Blueprint, redirect, render_template, request, session, url_for, jsonify, flash
from app.db_utils import connect_db, get_cursor
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from app.sql import *
admin_blp = Blueprint(
    "admin", __name__, template_folder='templates/admin', static_folder='static')


@admin_blp.route('/home')
def admin_home():
    return render_template('admin_home.html')

@admin_blp.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('auth.login'))
@admin_blp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html', title='Dashboard')


@admin_blp.route('/manage_rooms')
def room():
    conn = connect_db()
    cursor = get_cursor(conn)
    phong=''
    try:
        cursor.execute('select phong.room_id, phong.room_name,room_address, room_performence, room_price,loaiphong.room_name as "room_type" ,province_name, room_isdelete from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province where phong.room_isdelete = 1 order by phong.room_id;')
        conn.commit()
        phong = cursor.fetchall()
    except:
        conn.rollback()
    final_data = []
    for row in phong:
        temp = {}
        temp['room_id'] = row[0]
        temp['room_name'] = row[1]
        temp['room_address'] = row[2]
        temp['room_performance'] = row[3]
        temp['room_price'] = row[4]
        temp['room_type'] = row[5]
        temp['room_province'] = row[6]
        temp['room_isdelete'] = 'Active'

        final_data.append(temp)
    conn.close()
    # print(final_data)
    return render_template('admin/room.html', data = final_data)
@admin_blp.route('/edit_room/<id>', methods=['GET','POST'])
def edit_room(id):
    conn = connect_db()
    cursor = get_cursor(conn)
    phong = ''
    try:
        cursor.execute('select phong.room_id, phong.room_name,room_address, room_performence, room_price,loaiphong.room_name as "room_type" ,province_name from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province where phong.room_id = %s;', (id,))
        conn.commit()
    except:
        conn.rollback()

    phong = cursor.fetchone()
    # print(phong)

    temp = {}
    temp['room_id'] = phong[0]
    temp['room_name'] = phong[1]
    temp['room_address'] = phong[2]
    temp['room_performance'] = phong[3]
    temp['room_price'] = phong[4]
    temp['room_type'] = phong[5]
    temp['room_province'] = phong[6]
    conn.close()
    return render_template('edit_room.html', row=temp)

@admin_blp.route('/edit_room_submit', methods=['GET','POST'])
def edit_room_submit():

    conn = connect_db()
    cursor = get_cursor(conn)
    room_id = request.args.get('room_id')
    room_name = request.args.get('room_name')
    room_address = request.args.get('room_address')
    room_performance = request.args.get('room_performance')
    room_type = request.args.get('room_type')
    room_price = request.args.get('room_price')
    room_province = request.args.get('room_province')
    print(room_type, room_province, room_id)
    
    # print(id_type, id_province)
    try:
        
        sql1 = '''select room_id from loaiphong where room_name like "%{}%" '''
        cursor.execute(sql1.format(room_type))
        conn.commit()
        id_type = cursor.fetchone()
        print('catch id_type', id_type[0])
        sql2 = '''select province_id from tinhthanh where province_name like "%{}%"'''
        cursor.execute(sql2.format(room_province))
        conn.commit()
        id_province = cursor.fetchone()
        print('catch id_province', str(id_province))
        cursor.execute('''UPDATE `phong` SET `room_name` = %s, `room_address` = %s, `room_performence` = %s, `room_price` = %s, `id_roomtype` = %s, `id_province` = %s WHERE `room_id` = %s;''', 
        (room_name, room_address, room_performance, room_price, id_type[0],id_province[0], room_id ))
        conn.commit()
        print("Update successful")
        conn.close()
        return redirect ('/manage_rooms')
    except:
        print("Update unsuccessful")
        conn.rollback()
    return redirect(url_for('admin.edit_room', id=room_id))

@admin_blp.route('/room_filter')
def filter():
    conn = connect_db()
    cursor = get_cursor(conn)
    phong=''
    id_filter = request.args.get('id_filter')
    show_option = request.args.get('show_option')
    if show_option == 'showall':
        try:
            cursor.execute('select phong.room_id, phong.room_name,room_address, room_performence, room_price,loaiphong.room_name as "room_type" ,province_name, room_isdelete from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province  order by phong.room_id')
            conn.commit()
            phong = cursor.fetchall()
        except:
            conn.rollback()
    elif show_option == 'toanbo':
        try:
            cursor.execute('select phong.room_id, phong.room_name,room_address, room_performence, room_price,loaiphong.room_name as "room_type" ,province_name, room_isdelete from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province where phong.room_isdelete = 1 order by phong.{};'.format(id_filter,))
            conn.commit()
            phong = cursor.fetchall()
        except:
            conn.rollback()
    else:
        
    final_data = []
    for row in phong:
        temp = {}
        temp['room_id'] = row[0]
        temp['room_name'] = row[1]
        temp['room_address'] = row[2]
        temp['room_performance'] = row[3]
        temp['room_price'] = row[4]
        temp['room_type'] = row[5]
        temp['room_province'] = row[6]
        if row[7] == b'\x00':
            temp['room_isdelete'] = 'UNACTIVE'
        else:
            temp['room_isdelete'] = 'ACTIVE'
        final_data.append(temp)
    conn.close()
    # print(final_data)
    return render_template('admin/room.html', data = final_data)
@admin_blp.route('/delete_room/<id>', methods=['POST', 'GET'])
def delete_room(id):
    conn = connect_db()
    cursor = get_cursor(conn)
    sql = 'update phong set room_isdelete = 0 where room_id = %s'
    cursor.execute(sql, (id,))
    conn.commit()
    return redirect('/manage_rooms')

@admin_blp.route('/add_room')
def add_room():
    return render_template('admin/add_room.html')
    

@admin_blp.route('/add_room_submit')
def submit_room():
    if request.method == 'get':
        roomName = request.form['roomName']
        roomAddress = request.form['roomAddress']
        roomPrice = request.form['roomPrice']
        roomIntroduction = request.form['roomIntroduction']
        roomProvince = request.form['roomProvince']
        roomType = request.form['roomType']
        print(roomAddress)
    # Check if room existed
        conn = connect_db()
        cursor = get_cursor(conn)
        # sql = '''SELECT * FROM PHONG WHERE phong.room_name like "%{}%" or phong.room_address like "%{}%"'''
        # cursor.execute(sql, (roomName, roomAddress,))
        # conn.commit()
        # # room = cursor.fetchone()
        # # conn.close()
        # conn = connect_db()
        # cursor = get_cursor(conn)
        # Get province ID
        sql1 = '''SELECT province_id from tinhthanh where tinhthanh.province_name like "%{}%";'''
        cursor.execute(sql1,(roomPrice,))
        conn.commit()
        idProvince = cursor.fetchone()
        sql2 = '''SELECT room_id from loaiphong where loaiphong.room_name like "%{}%"'''
        cursor.execute(sql2,(roomType,))
        conn.commit()
        id_type = cursor.fetchone()
        sql3 ='''INSERT INTO phong values (NULL, %s, %s, %s, %s, %s, %s, 0)'''
        cursor.execute(sql3,(roomName, roomAddress, roomIntroduction, roomPrice, id_type, idProvince,))
        flash('Error')
        return('/manage_rooms')
    flash("error")
    return redirect('/add_room')
@admin_blp.route("/ajaxpost",methods=["POST","GET"])
def ajaxpost():
    conn = connect_db()
    cursor = get_cursor(conn)
    if request.method == 'POST':
        queryString = request.form['queryString']
        print(queryString)
        query = "SELECT * from tinhthanh WHERE province_name LIKE '%{}%' LIMIT 10".format(queryString)
        cursor.execute(query)
        tinhthanh = cursor.fetchall()
    return jsonify({'htmlresponse': render_template('admin/response/response_province.html', tinhthanh=tinhthanh)})
@admin_blp.route("/type_room_ajax",methods=["POST","GET"])
def type_room_ajax():
    conn = connect_db()
    cursor = get_cursor(conn)
    if request.method == 'POST':
        queryString = request.form['queryString']
        print(queryString)
        query = "SELECT * from loaiphong WHERE room_name LIKE '%{}%' LIMIT 10".format(queryString)
        cursor.execute(query)
        loaiphong = cursor.fetchall()
    return jsonify({'htmlresponse': render_template('admin/response/response_roomtype.html', loaiphong=loaiphong)})
@admin_blp.route("/ajaxlivesearch",methods=["POST","GET"])
def ajaxlivesearch():
    conn = connect_db()
    cur = get_cursor(conn)
    if request.method == 'POST':
        search_word = request.form['query']
        print(search_word)
        if search_word == '':
            cur.execute('select phong.room_id, room_address, room_performence, room_price,loaiphong.room_name as "room_type" ,province_name from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province where phong.room_isdelete = 1 order by phong.room_id;')
            room = cur.fetchall()
        else:    
            query = '''select phong.room_id, room_address, room_performence, room_price, loaiphong.room_name as room_type ,province_name from phong inner join loaiphong on loaiphong.room_id = phong.id_roomtype inner join tinhthanh on tinhthanh.province_id = phong.id_province 
WHERE room_address LIKE %s OR room_performence LIKE %s OR loaiphong.room_name LIKE %s  OR  province_name like %s ORDER BY phong.room_id DESC LIMIT 20''', (search_word,search_word, search_word, search_word, )
            cur.execute(query)
            numrows = int(cur.rowcount)
            room = cur.fetchall()
            print(numrows)
    final_data = []
    for row in room:
        temp = {}
        temp['room_id'] = row[0]
        temp['room_name'] = row[1]
        temp['room_address'] = row[2]
        temp['room_performance'] = row[3]
        temp['room_price'] = row[4]
        temp['room_type'] = row[5]
        # temp['room_province'] = row[6]
        final_data.append(temp)
    return jsonify({'htmlresponse': render_template('admin/room.html', room=room)})

@admin_blp.route('/customer')
def customer():
    pass


@admin_blp.route('/convenient')
def convenient():
    pass


@admin_blp.route('/service')
def service():
    pass
