from flask import Flask, flash, render_template, request, redirect, session, escape
from data_manager import save_user, accept_answer
import data_manager
import os, bcrypt


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/list", methods=['GET', "POST"])
@app.route("/list/<sorted>/<sort>", methods=["GET"])
def list_questions(sorted='vote_number', sort='DESC'):
    questions = data_manager.get_all(sorted, sort)
    tags = data_manager.get_all_comment("tags")
    user_id = 8721544
    if session:
        logged_in = True
        user_id = session["user_id"]
    else:
        logged_in = False
    return render_template("list_questions.html", logged_in=logged_in, questions=questions, tags=tags, user_id=user_id)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/question/<index_of_que>/<user_id>", methods=['GET', 'POST'])
def question_write(index_of_que, user_id):
    data_manager.view_num_add(index_of_que)
    question = data_manager.get_que(index_of_que)
    question_comments = data_manager.get_all_comment("comments_questions")
    answers = data_manager.get_all_answers(index_of_que)
    answer_comments = data_manager.get_all_comment("comments_answers")  # session['id'] # itt kéne ez a cucc, de
    if session:
        logged_in = True
        signed_id = session["user_id"]
    else:
        logged_in = False
        signed_id = 0
    return render_template("answers.html", logged_in=logged_in, answers=answers, question=question, id=index_of_que, question_comments=question_comments, answer_comments=answer_comments, creater_id=user_id, signed_id=signed_id)


@app.route("/vote_answer/<int:answer_id>/<question_id>/<int:user_id>/<int:creater_id>", methods=["GET", "POST"])
def vote_answer(answer_id, question_id, user_id, creater_id):
    if request.method == "POST":
        if request.form.get("up", "valami") == "up":
            old_reputation = data_manager.read_reputation(user_id)[0][0]
            new_reputation = old_reputation + 10
            data_manager.update_reputation(new_reputation, user_id)
            data_manager.vote_update_plus(answer_id, "answers")
        elif request.form.get("down", "valami") == "down":
            old_reputation = data_manager.read_reputation(user_id)[0][0]
            new_reputation = old_reputation -2
            data_manager.update_reputation(new_reputation, user_id)
            data_manager.vote_update_minus(answer_id, "answers")
        data_manager.view_num_minus(question_id)
        return redirect(f"/question/{question_id}/{creater_id}")
    return redirect("/question/<question_id>/<creater_id>")


@app.route("/vote/<int:question_id>/<int:user_id>", methods=["POST"])
def vote(question_id, user_id):
    if request.form.get("up", "valami") == "up":
        old_reputation = data_manager.read_reputation(user_id)[0][0]
        new_reputation = old_reputation + 5
        data_manager.update_reputation(new_reputation, user_id)
        data_manager.vote_update_plus(question_id, "questions")
    elif request.form["down"] == "down":
        old_reputation = data_manager.read_reputation(user_id)[0][0]
        new_reputation = old_reputation - 2
        data_manager.update_reputation(new_reputation, user_id)
        data_manager.vote_update_minus(question_id, "questions")
    referer = request.headers.get("Referer")
    return redirect(referer)


@app.route("/uploadfile_question", methods=["GET", "POST"])
def uploadfile_question():
    questions = data_manager.get_all(sorted="id", sort="ASC")
    question_indexes = []
    for index in range(len(questions)):
        question_indexes.append(int(questions[index][0]))
    new_id = max(question_indexes)+1
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    if request.method == "POST":
        file_barmimas = request.files['file']
        if file_barmimas.filename != ' ':
            file_barmimas.save(os.path.join(PROJECT_ROOT, "static", "Picture", "questions_pics", str(new_id) + ".jpeg"))
    return redirect("/add-question")


@app.route("/sort")
def sort_list():
    sort = "DESC"
    if request.args.get == "title":
        sorted = "title"
        return redirect(f"/list/{sorted}/{sort}")
    elif request.args.get("sorting") == "sub_time":
        sorted = "submission"
        return redirect(f"/list/{sorted}/{sort}")
    elif request.args.get("sorting") == "message":
        sorted = "message_"
        return redirect(f"/list/{sorted}/{sort}")
    elif request.args.get("sorting") == "num_of_views":
        sorted = "view_number"
        return redirect(f"/list/{sorted}/{sort}")
    elif request.args.get("sorting") == "num_of_votes":
        sorted = "vote_number"
        return redirect("/list")


@app.route("/add-question/<user_id>", methods=["GET"])
def new_question_page_render(user_id):
    return render_template("add_new_question.html", user_id=user_id)


@app.route("/like")
def like_button():
    like_data_file = open("sample_data/site_likes.txt", "r")
    like_number = like_data_file.read()
    like_data_file.close()
    likes = int(like_number) + 1
    likes = str(likes)
    write_like_data = open("sample_data/site_likes.txt", "w")
    write_like_data.write(likes)
    write_like_data.close()
    return redirect(request.referrer)


@app.route("/")
def render_main_page():
    username = ""
    print(session)
    user_id = 13413134314141241231232131231253531213123123
    if session:
        logged_in = True
        username = session["username"]
        user_id = session["user_id"]

    else:
        logged_in = False
    like_data_file = open("sample_data/site_likes.txt", "r")
    like_number = like_data_file.read()
    list_of_questions = data_manager.list_last_5()
    return render_template("index.html", likes=like_number, list=list_of_questions, logged_in=logged_in, username=username, user_id=user_id)


@app.route("/edit_question/<question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    question = data_manager.get_que(question_id)
    return render_template("edit_question.html", id=question_id, question=question)


# submit new question
@app.route("/submit", methods=["POST"])
def submit():
    new_question = []
    new_id = 1
    # id generator:
    questions = data_manager.get_all("id", "ASC")
    question_indexes = []
    if questions:
        for index in range(len(questions)):
            question_indexes.append(int(questions[index][0]))
        new_id = max(question_indexes)+1
    new_question.append(new_id)
    new_question.append(format(request.form['subject']))
    new_question.append(format(request.form['new_question']))
    new_question.append(str(new_id))
    new_question.append(format(request.form['user_id']))
    tag = format(request.form['tag'])
    tags = data_manager.get_tags()
    tag_id = []
    new_tag_id = 1
    if tag != None:
        for i in tags:
            tag_id.append(int(i[0]))
        if tag_id:
            new_tag_id = max(tag_id)+1
    data_manager.give_tag(new_tag_id, tag, new_id)
    data_manager.save_question(new_question)
    return redirect("/list")


@app.route("/answerdelete/<int:answer_id>/<int:index_of_que> ", methods=["POST"])
def answerdelete(answer_id, index_of_que):
    data_manager.delete_answer(answer_id, index_of_que)
    return redirect(f"/question/{index_of_que}")


@app.route("/add_new_answer/<question_id>/<user_id>", methods=["POST"])
def add_new_answer(question_id, user_id):
    # <!--id;submission_time;vote_number;question_id;message;image-->
    answer = data_manager.get_all_comment("answers") # Itt nem csak a kommenteket lehet megkapni hanem az atributumban szereplő table-ből mindent
    new_answer = []
    answer_message = format(request.form['new_answer'])
    answer_indexes = []
    new_id = 1
    if answer:
        for index in range(len(answer)):
            answer_indexes.append(int(answer[index][0]))
        new_id = max(answer_indexes) + 1
    new_answer.append(str(new_id))
    # vote_number
    new_answer.append(str(question_id))
    new_answer.append(answer_message)
    new_answer.append("")
    new_answer.append(int(user_id))
    data_manager.save_answers(new_answer)
    return redirect(f"/question/{question_id}/{user_id}")


@app.route("/new_answer/<question_id>/<user_id>/", methods=["POST"])
def new_answer(question_id, user_id):
    return render_template("add_new_answer.html", question_id=question_id, user_id=user_id)


@app.route("/edit_que/<index_of_que>",  methods=["POST"])
def edit_que(index_of_que):
    updated_que = []
    updated_que.append(format(request.form['subject']))
    updated_que.append(format(request.form['new_question']))
    data_manager.update_que(index_of_que, updated_que)
    return redirect(f"/question/{index_of_que}")


@app.route("/delete_que/<index_of_que>")
def delete_que(index_of_que):
    data_manager.delete_question(index_of_que)
    return redirect("/list")


@app.route('/search', methods=['POST', 'GET'])
def search_input():
    list_of_q_id = []
    list_of_a_id = []
    userinput = request.args.get('userinput')
    questions_contain = data_manager.get_search_que(userinput)
    for line in questions_contain:
        list_of_q_id.append(line[0])
    answer_contain = data_manager.get_search_ans(userinput)
    for line in answer_contain:
        list_of_a_id.append(line[3])
    if len(list_of_a_id) > len(list_of_q_id):
        for i in list_of_a_id:
            if i not in list_of_q_id:
                questions_contain.append("".join(data_manager.get_que(i)))
    for i in range(len(questions_contain)):
        questions_contain[i] = list(questions_contain[i])
    for i in range(len(answer_contain)):
        answer_contain[i] = list(answer_contain[i])
    return render_template('search.html', userinput=userinput, questions=questions_contain, answers=answer_contain)


@app.route("/contact")
def render_contact_page():
    return render_template("contact_us.html", logged_in=False)


@app.route("/delete_tag/<id>")
def delete_tag(id):
    data_manager.delete_tag_(id)
    return redirect("/list")


@app.route("/new_comment_question/<question_id>/<user_id>")
def new_comment_question(question_id, user_id):
    return render_template("new_comment_question.html", question_id=question_id, user_id=user_id)


@app.route("/save_comment/<question_id>/<user_id>", methods=["POST"])
def save_comment_question(question_id, user_id):
    comm_que = data_manager.get_all_comment("comments_questions")
    comm_id = []
    new_comm_id = 1
    if comm_que:
        for i in comm_que:
            comm_id.append(i[0])
        new_comm_id = max(comm_id)+1
    comment = format(request.form["comments_question"])
    data_manager.save_comm_que(new_comm_id, comment, question_id, user_id)
    return redirect(f"/question/{question_id}")


@app.route("/new_comment_answer/<answer_id>/<user_id>")
def new_comment_answer(answer_id, user_id):
    return render_template("new_comment_answer.html", answer_id=answer_id, user_id=user_id)


@app.route("/save_comm_answr/<answer_id>/<user_id>", methods=["POST"])
def save_comm_answr(answer_id):
    comm_ans = data_manager.get_all_comment("comments_answers")
    comm_id = []
    new_comm_id = 1
    if comm_ans:
        for i in comm_ans:
            comm_id.append(i[0])
        new_comm_id = max(comm_id)+1
    comment = format(request.form["comments_answer"])
    data_manager.save_comm_ans(new_comm_id, comment, answer_id, user_id)
    return redirect("/list")


@app.route("/del_com_que/<id>")
def del_com_que(id):
    data_manager.del_com(id, "comments_question")
    return redirect("/list")


@app.route("/del_com_ans/<id>")
def del_com_ans(id):
    data_manager.del_com(id, "answer_question")
    return redirect("/list")


@app.route("/edit_comment_answer/<id>")
def edit_comment_answer(id):
    answer = ""
    answers = data_manager.get_all_comment("comments_answers")
    for i in answers:
        if str(i[0]) == id:
            answer = i
    return render_template("edit_com_a.html", answer=answer)


@app.route("/edit_anser_com_save/<id>", methods=["POST"])
def edit_anser_com_save(id):
    title = format(request.form["saved_com"])
    data_manager.update_com_an(id, "comments_answers", title)
    return redirect("/list")


@app.route("/edit_comment_question/<id>")
def edit_comment_question(id):
    question = ""
    questions = data_manager.get_all_comment("comments_questions")
    for i in questions:
        if str(i[0]) == id:
            question = i
    return render_template("edit_com_q.html", question=question)


@app.route("/edit_quest_com_save/<id>", methods=["POST"])
def edit_quest_com_save(id):
    title = format(request.form["saved_com"])
    data_manager.update_com_qu(id, "comments_questions", title)
    return redirect("/list")


@app.route("/add_new_tag/<id>", methods=["POST"])
def add_new_tag(id):
    tags = data_manager.get_tags()
    id_list = []
    new_id = 1
    for i in tags:
        id_list.append(i[0])
    if id_list:
        new_id = max(id_list)+1
    title = format(request.form["tag"])
    data_manager.give_tag(new_id, title, id)
    return(redirect(f"/edit_question/{id}"))


@app.route("/registration", methods=["POST", "GET"])
def registration():
    users = data_manager.read_user_info()
    message = ""
    if request.method == "POST":
        username = request.form["new_user"]
        email = request.form["new_email"] 
        password = request.form["new_user_pw"]

        username_list = [username[1] for username in users]
        if username not in username_list or not username_list:
            message = "Registration successful!"
            save_user(username,email,password)
        else:
            message = "Username or email already taken!"
    return render_template("reg.html", message = message)


@app.route('/logout')
def logout():
    session.pop('username')
    session.pop('pw')
    session.pop('user_id')
    return redirect("/")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        users = data_manager.read_user_info()
        message = ""
        username = request.form['user']
        password = request.form['pw']
        correct_pw_database = data_manager.get_pw(username)
        correct_pw = correct_pw_database[0][0]
        hashed_pw = bcrypt.hashpw(correct_pw.encode('utf-8'), bcrypt.gensalt())
        user_id_list = [user_id[0] for user_id in users]
        username_list = [username[1] for username in users]

        if username in username_list:
            index = username_list.index(username)
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
                user_id_index = user_id_list[index]
                session['username'] = request.form['user']
                session['pw'] = request.form['pw']
                session['user_id'] = user_id_index
                message = "Login successful!"
            else:
                message = "Incorrect username or password!"
        else:
            message = "User does not exist!"
        return render_template("login.html", message=message)


@app.route("/users")
def list_users():
    users = data_manager.read_user_info()
    return render_template("users_list.html", users=users, logged_in=True)


@app.route("/user/<user_id>")
def user(user_id):  # original def name user_profile_page
    # User Profile Page
    questions = data_manager.read_questions()
    users = data_manager.read_user_info()
    answers = data_manager.read_answers()
    question_comments = data_manager.read_question_comments()
    answer_comments = data_manager.read_answer_comments()
    return render_template("profile_page.html", id=int(user_id), users=users, questions=questions, answers=answers, question_comments=question_comments, answer_comments=answer_comments)


@app.route("/accept/<answer_id>/<question_id>/<user_id>")
def accept(answer_id, question_id, user_id):
    reputation_to_accept = data_manager.read_reputation_and_to_answer_accept(question_id, answer_id)
    new_reputation = int(reputation_to_accept[0][0]) + 15
    data_manager.update_reputation(new_reputation, reputation_to_accept[0][1])
    accept_answer(answer_id)
    return redirect(f"/question/{question_id}/{user_id}")


@app.route("/tags")
def tags_page():
    tags = data_manager.tag_counter()
    return render_template("tags_page.html", tags=tags)


if __name__ == "__main__":
    app.run(
        debug=True,  # Allow verbose error reports
        port=5000  # Set custom port
        )
