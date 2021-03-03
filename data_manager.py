import os
import psycopg2
from psycopg2.extensions import AsIs
import bcrypt


def user():
    lineuser = []
    with open("user.txt", "r") as user_db:
        lineuser = user_db.readline().split(",")
    return lineuser


def get_alonescursor():
    data = user()
    con = psycopg2.connect(database=data[0], user=data[1], password=data[2], host=data[3], port=data[4])
    con.autocommit = True
    return con.cursor()


def get_all(sorted, sort):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM questions ORDER BY %(sorted)s %(sort)s;",
                   {'sorted': AsIs(sorted), 'sort': AsIs(sort)})
    result = cursor.fetchall()
    return result


#print(get_all(sorted, sort='DESC'))

def get_all_answers(id):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM answers WHERE question_id = %(q_id)s", {"q_id": id})
    result = cursor.fetchall()
    return result


def get_que(id):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM questions WHERE id = %(id)s", {"id": id})
    result = cursor.fetchall()
    return result


def vote_update_plus(id, table_name):
    cursor = get_alonescursor()
    cursor.execute("UPDATE %(table_name)s SET vote_number = vote_number + 1 WHERE id = %(id)s",
                   {"table_name": AsIs(table_name), "id": id})


def vote_update_minus(id, table_name):
    cursor = get_alonescursor()
    cursor.execute("UPDATE %(table_name)s SET vote_number = vote_number - 1 WHERE id = %(id)s",
                   {"table_name": AsIs(table_name), "id": id})


''' Read and Write CSV files'''

'''# Read CSV files to NestedList
# Need file name, because it could handle all CSV file
# File_name needs to contains the ".txt" too'''


def read_csv_files(file_name, separate=';'):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(file_name))
    QUESTION_FILE_PATH = os.path.join(PROJECT_ROOT, 'sample_data', file_name)
    # list for converting to a nested list
    converted_file = []
    with open(QUESTION_FILE_PATH, "r") as csv_file:
        lines = csv_file.readlines()
        # add lines to the list and split unusefull characters
        for elements in lines:
            converted_file.append(elements.replace("\n", "").split(separate))
    # return nested list
    return converted_file


'''function for write to CSV file
#Am i need to make headers?????'''


def convert_to_csv_file(file_name, list_to_convert, separate=';'):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(file_name))
    QUESTION_FILE_PATH = os.path.join(PROJECT_ROOT, 'sample_data', file_name)
    with open(QUESTION_FILE_PATH, "w") as CSV_file:
        # loop what makes the csv format
        line = ""
        for items in list_to_convert:
            line = separate.join(items)
            CSV_file.write(line + "\n")


def list_last_5():
    cursor = get_alonescursor()
    cursor.execute("SELECT * from questions order by id desc limit 5;")
    result = cursor.fetchall()
    return result


def save_question(line):
    cursor = get_alonescursor()
    cursor.execute("UPDATE users_info SET question_count = question_count + 1 WHERE id = %(id)s ", {"id": line[4]})
    cursor.execute("INSERT INTO questions (id, view_number, vote_number, title, message_, image_name, user_id) VALUES (%(id)s, 0, 0, %(title)s, %(message)s, %(image_name)s, %(user_id)s);", {"id": line[0], "title": line[1], "message": line[2], "image_name": str(line[3]), "user_id": line[4]})


def delete_question(index):
    curs = get_alonescursor()
    curs.execute("DELETE FROM questions WHERE id=%(index)s;", {"index": index})
    curs.execute("DELETE FROM answers WHERE question_id = %(index)s", {"index": index})


def update_que(id, update_list):
    cursor = get_alonescursor()
    cursor.execute("UPDATE questions SET title = %(title)s, message_ = %(message)s WHERE id = %(id)s",
                   {"title": update_list[0], "message": update_list[1], "id": id})


def view_num_add(id):
    cursor = get_alonescursor()
    cursor.execute("UPDATE questions SET view_number = view_number + 1 WHERE id = %(id)s", {"id": id})


def view_num_minus(id):
    cursor = get_alonescursor()
    cursor.execute("UPDATE questions SET view_number = view_number - 1 WHERE id = %(id)s", {"id": id})


def get_search_que(search):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM questions WHERE title LIKE '%{}%' OR message_ LIKE '%{}%';".format(search, search))
    result = cursor.fetchall()
    return result


def get_search_ans(search):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM answers WHERE message_ LIKE '%{}%';".format(search))
    result = cursor.fetchall()
    return result


def save_answers(line):
    cursor = get_alonescursor()
    cursor.execute("UPDATE users_info SET answer_count = answer_count + 1 WHERE id = %(id)s ", {"id": line[4]})
    cursor.execute("INSERT INTO answers (id, sub_time, vote_number, question_id, message_, image_name, user_id) VALUES (%(id)s, %(submission_time)s, 0, %(question_id)s, %(message_)s, %(image_name)s, %(user_id)s);", {"id": line[0], "submission_time": line[1], "question_id": line[2], "message_": line[3],"image_name": str(line[4]), "user_id": line[4]})


def delete_answer(id, question_id):
    curs = get_alonescursor()
    curs.execute("DELETE FROM answers WHERE id=%(id)s AND question_id=%(question_id)s;",
                 {"id": id, "question_id": question_id})


def give_tag(id, title, question_id):
    cursor = get_alonescursor()
    cursor.execute("INSERT INTO tags (id, title, question_id) VALUES (%(id)s, %(title)s, %(question_id)s);",
                   {"id": id, "title": title, "question_id": question_id})


def get_tags():
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM tags;")
    result = cursor.fetchall()
    return result


def delete_tag_(id):
    cursor = get_alonescursor()
    cursor.execute("DELETE FROM tags WHERE id = %(id)s", {"id": id})


def get_all_comment(filename):
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM %(filename)s", {"filename": AsIs(filename)})
    result = cursor.fetchall()
    return result


def save_comm_que(id, title, question_id, user_id):
    cursor = get_alonescursor()
    cursor.execute("UPDATE users_info SET answer_cout = answer_count + 1 WHERE id = %(user_id)s", {"user_id": user_id})
    cursor.execute("INSERT INTO comments_questions (id, title, question_id, user_id) VALUES (%(id)s,%(title)s,%(question_id)s, %(user_id)s);",
    {"id": id, "title": title, "question_id": question_id, "user_id": user_id})


def save_comm_ans(id, title, answer_id, user_id):
    cursor = get_alonescursor()
    cursor.execute("UPDATE users_info SET answer_cout = answer_count + 1 WHERE id = %(user_id)s", {"user_id": user_id})
    cursor.execute("INSERT INTO comments_answers (id, title, answer_id, user_id) VALUES (%(id)s,%(title)s,%(answer_id)s, %(user_id)s);",
                   {"id": id, "title": title, "answer_id": answer_id, "user_id": user_id})


def del_com(id, filename):
    cursor = get_alonescursor()
    cursor.execute("DELETE FROM %(filename)s WHERE id = %(id)s", {"filename": AsIs(filename), "id": id})


def update_com_qu(id, filename, title):
    cursor = get_alonescursor()
    cursor.execute("UPDATE %(filename)s SET title = %(title)s WHERE question_id = %(id)s",
                   {"filename": AsIs(filename), "id": id, "title": title})


def update_com_an(id, filename, title):
    cursor = get_alonescursor()
    cursor.execute("UPDATE %(filename)s SET title = %(title)s WHERE answer_id = %(id)s",
                   {"filename": AsIs(filename), "id": id, "title": title})


def save_user(username, email, pw):
    cursor = get_alonescursor()
    cursor.execute(
        'INSERT INTO users_info(username, email, password, reputation, question_count, answer_count, comment_count) values(%(username)s, %(email)s, %(pw)s, 0, 0, 0, 0);',
        {'username': username, 'email': email, 'pw': pw})

def read_user_info():
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM users_info ")
    result = cursor.fetchall()
    return result


def read_reputation():
    cursor = get_alonescursor()
    cursor.execute("SELECT reputation, id FROM users_info ")
    reputation_and_user = cursor.fetchall()
    return reputation_and_user


print(read_reputation())


def read_questions():
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM questions")
    result = cursor.fetchall()
    return result


def read_answers():
    cursor = get_alonescursor()
    cursor.execute("SELECT * FROM answers")
    result = cursor.fetchall()
    return result

##PASSWORD HATCHING


def hash_password(plain_text_password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def read_question_comments():
    cursor = get_alonescursor()
    cursor.execute("SELECT questions.user_id AS creater_id, questions.id, comments_questions.title, comments_questions.user_id FROM questions JOIN comments_questions ON(questions.id = comments_questions.question_id)")
    result = cursor.fetchall()
    return result


def read_answer_comments():
    cursor = get_alonescursor()
    cursor.execute("SELECT questions.user_id AS creater_id, questions.id, comments_answers.title, comments_answers.user_id FROM questions JOIN answers ON(questions.id = answers.question_id) JOIN comments_answers ON(answers.id = comments_answers.answer_id)" )
    answer_comments = cursor.fetchall()
    return answer_comments
