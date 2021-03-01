from flask import Flask, flash, render_template, request, redirect
from data_manager import read_csv_files, convert_to_csv_file, get_all
from data_manager import get_all_answers, get_que, vote_update_minus
from data_manager import vote_update_plus, save_question, update_que
from data_manager import view_num_add, delete_question, del_com
from data_manager import list_last_5, view_num_minus, update_com_qu
from data_manager import update_com_an
from data_manager import view_num_add, delete_question, save_answers, delete_answer
from data_manager import get_search_que, get_tags, give_tag, delete_tag_
from data_manager import get_search_ans, save_answers, get_all_comment
from data_manager import save_comm_ans, save_comm_que
import data_manager
import os
from list_breaker import list_sorter, view_number_adder
from list_breaker import view_number_minuser, cut_out_for_edit
import datetime


app = Flask(__name__)


@app.route("/list", methods=['GET', "POST"])
@app.route("/list/<sorted>/<sort>", methods=["GET"])
def list_questions(sorted='vote_number', sort='DESC'):
    questions = get_all(sorted, sort)
    tags = get_all_comment("tags")
    return render_template("list_questions.html", questions=questions, tags=tags)


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/question/<index_of_que>", methods=['GET', 'POST'])
def question_write(index_of_que):
    view_num_add(index_of_que)
    question = get_que(index_of_que)
    question_comments = get_all_comment("comments_questions")
    answers = get_all_answers(index_of_que)
    answer_comments = get_all_comment("comments_answers")
    return render_template("answers.html", answers=answers, question=question, id=index_of_que, question_comments=question_comments, answer_comments=answer_comments)


@app.route("/vote_answer/<int:answer_id>/<question_id>", methods=["GET", "POST"])
def vote_answer(answer_id, question_id):
    if request.method == "POST":
        if request.form.get("up", "valami") == "up":
            vote_update_plus(answer_id, "answers")
        elif request.form.get("down", "valami") == "down":
            vote_update_minus(answer_id, "answers")
        view_num_minus(question_id)
        return redirect(f"/question/{question_id}")
    return redirect("/question/<question_id>")


@app.route("/vote/<int:question_id>", methods=["POST"])
def vote(question_id):
    if request.form.get("up", "valami") == "up":
        vote_update_plus(question_id, "questions")
    elif request.form["down"] == "down":
        vote_update_minus(question_id, "questions")
    referer = request.headers.get("Referer")
    return redirect(referer)


@app.route("/uploadfile_question", methods=["GET", "POST"])
def uploadfile_question():
    questions = get_all(sorted="id", sort="ASC")
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


@app.route("/add-question", methods=["GET"])
def new_question_page_render():
    return render_template("add_new_question.html")


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
    like_data_file = open("sample_data/site_likes.txt", "r")
    like_number = like_data_file.read()
    list_of_questions = list_last_5()
    return render_template("index.html", likes=like_number, list = list_of_questions)


@app.route("/edit_question/<question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    question = get_que(question_id)
    return render_template("edit_question.html", id=question_id, question=question)


# submit new question
@app.route("/submit", methods=["POST"])
def submit():
    new_question = []
    new_id = 1
    # id generator:
    questions = get_all("id", "ASC")
    question_indexes = []
    if questions:
        for index in range(len(questions)):
            question_indexes.append(int(questions[index][0]))
        new_id = max(question_indexes)+1
    new_question.append(new_id)
    new_question.append(format(request.form['subject']))
    new_question.append(format(request.form['new_question']))
    new_question.append(str(new_id))
    tag = format(request.form['tag'])
    tags = get_tags()
    tag_id = []
    new_tag_id = 1
    if tag != None:
        for i in tags:
            tag_id.append(int(i[0]))
        if tag_id:
            new_tag_id = max(tag_id)+1
    give_tag(new_tag_id, tag, new_id)
    save_question(new_question)
    return redirect("/list")


@app.route("/answerdelete/<int:answer_id>/<int:index_of_que> ", methods=["POST"])
def answerdelete(answer_id, index_of_que):
    delete_answer(answer_id, index_of_que)
    return redirect(f"/question/{index_of_que}")


@app.route("/add_new_answer/<question_id>", methods=["POST"])
def add_new_answer(question_id):
    # <!--id;submission_time;vote_number;question_id;message;image-->
    answer = get_all_comment("answers") # Itt nem csak a kommenteket lehet megkapni hanem az atributumban szereplő table-ből mindent
    new_answer = []
    answer_message = format(request.form['new_answer'])
    now = datetime.datetime.now()
    date_tuple = now.year, now.month, now.day, now.hour, now.minute
    date_list = [str(date_tuple[0]), "." ,str(date_tuple[1]),".",str(date_tuple[2])," ",str(date_tuple[3]),":",str(date_tuple[4])]
    date = ''.join(date_list)
    answer_indexes = []
    new_id = 1
    if answer:
        for index in range(len(answer)):
            answer_indexes.append(int(answer[index][0]))
        new_id = max(answer_indexes) + 1
    new_answer.append(str(new_id))
    # date saver to implement
    new_answer.append(str(date))
    # view_number
    # new_answer.append(str(0))
    # vote_number
    new_answer.append(str(question_id))
    new_answer.append(answer_message)
    new_answer.append("")
    save_answers(new_answer)
    return redirect(f"/question/{question_id}")


@app.route("/new_answer/<question_id>", methods=["POST"])
def new_answer(question_id):
    return render_template("add_new_answer.html", question_id=question_id)


@app.route("/edit_que/<index_of_que>",  methods=["POST"])
def edit_que(index_of_que):
    updated_que = []
    updated_que.append(format(request.form['subject']))
    updated_que.append(format(request.form['new_question']))
    update_que(index_of_que, updated_que)
    return redirect(f"/question/{index_of_que}")


@app.route("/delete_que/<index_of_que>")
def delete_que(index_of_que):
    delete_question(index_of_que)
    return redirect("/list")


@app.route('/search', methods=['POST', 'GET'])
def search_input():
    list_of_q_id = []
    list_of_a_id = []
    userinput = request.args.get('userinput')
    questions_contain = get_search_que(userinput)
    for line in questions_contain:
        list_of_q_id.append(line[0])
    answer_contain = get_search_ans(userinput)
    for line in answer_contain:
        list_of_a_id.append(line[3])
    if len(list_of_a_id) > len(list_of_q_id):
        for i in list_of_a_id:
            if i not in list_of_q_id:
                questions_contain.append("".join(get_que(i)))
    for i in range(len(questions_contain)):
        questions_contain[i] = list(questions_contain[i])
    for i in range(len(answer_contain)):
        answer_contain[i] = list(answer_contain[i])
    return render_template('search.html', userinput=userinput, questions=questions_contain, answers=answer_contain)


@app.route("/contact")
def render_contact_page():
    return render_template("contact_us.html")


@app.route("/delete_tag/<id>")
def delete_tag(id):
    delete_tag_(id)
    return redirect("/list")


@app.route("/new_comment_question/<question_id>")
def new_comment_question(question_id):
    return render_template("new_comment_question.html", question_id=question_id)


@app.route("/save_comment/<question_id>", methods=["POST"])
def save_comment_question(question_id):
    comm_que = get_all_comment("comments_questions")
    comm_id = []
    new_comm_id = 1
    if comm_que:
        for i in comm_que:
            comm_id.append(i[0])
        new_comm_id = max(comm_id)+1
    comment = format(request.form["comments_question"])
    save_comm_que(new_comm_id, comment, question_id)
    return redirect(f"/question/{question_id}")


@app.route("/new_comment_answer/<answer_id>")
def new_comment_answer(answer_id):
    return render_template("new_comment_answer.html", answer_id=answer_id)


@app.route("/save_comm_answr/<answer_id>/", methods=["POST"])
def save_comm_answr(answer_id):
    comm_ans = get_all_comment("comments_answers")
    comm_id = []
    new_comm_id = 1
    if comm_ans:
        for i in comm_ans:
            comm_id.append(i[0])
        new_comm_id = max(comm_id)+1
    comment = format(request.form["comments_answer"])
    save_comm_ans(new_comm_id, comment, answer_id)
    return redirect("/list")


@app.route("/del_com_que/<id>")
def del_com_que(id):
    del_com(id, "comments_question")
    return redirect("/list")


@app.route("/del_com_ans/<id>")
def del_com_ans(id):
    del_com(id, "answer_question")
    return redirect("/list")

@app.route("/edit_comment_answer/<id>")
def edit_comment_answer(id):
    answer = ""
    answers = get_all_comment("comments_answers")
    for i in answers:
        if str(i[0]) == id:
            answer = i
    return render_template("edit_com_a.html", answer=answer)

@app.route("/edit_anser_com_save/<id>", methods=["POST"])
def edit_anser_com_save(id):
    title = format(request.form["saved_com"])
    update_com_an(id, "comments_answers", title)
    return redirect("/list")


@app.route("/edit_comment_question/<id>")
def edit_comment_question(id):
    question = ""
    questions = get_all_comment("comments_questions")
    for i in questions:
        if str(i[0]) == id:
            question = i
    return render_template("edit_com_q.html", question=question)

@app.route("/edit_quest_com_save/<id>", methods=["POST"])
def edit_quest_com_save(id):
    title = format(request.form["saved_com"])
    update_com_qu(id, "comments_questions", title)
    return redirect("/list")


@app.route("/add_new_tag/<id>", methods=["POST"])
def add_new_tag(id):
    tags = get_tags()
    id_list = []
    new_id = 1
    for i in tags:
        id_list.append(i[0])
    if id_list:
        new_id = max(id_list)+1     
    title = format(request.form["tag"])
    give_tag(new_id, title, id)
    return(redirect(f"/edit_question/{id}"))


@app.route("/registration")
def registration():
    return render_template("reg.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/users")
def list_users():
    users = data_manager.read_user_info()
    return render_template("users_list.html", users=users, logged_in=True)


if __name__ == "__main__":
    app.run(
        debug=True,  # Allow verbose error reports
        port=5000  # Set custom port
        )


