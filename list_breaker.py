# id,submission_time,view_number,vote_number,title,message,image
from data_manager import read_csv_files, convert_to_csv_file


def list_sorter(questions_list, check_index):
    if check_index == 1 or check_index == 2 or check_index == 3:
        new_list = sorted(questions_list, key=lambda x: int(x[check_index]), reverse=True)
        return new_list
    if check_index == 4 or check_index == 5:
        new_list = sorted(questions_list, key=lambda x: x[check_index], reverse=False)
        return new_list


def view_number_adder(index_to_add):
    questionss = read_csv_files("question.csv")
    for index, item in enumerate(questionss):
        if item[0] == index_to_add:
            questionss[index][2] = int(questionss[index][2])
            questionss[index][2] += 1
            questionss[index][2] = str(questionss[index][2])
    convert_to_csv_file("question.csv", questionss)


def view_number_minuser(index_to_minus):
    questionss = read_csv_files("question.csv")
    for index, item in enumerate(questionss):
        if item[0] == index_to_minus:
            questionss[index][2] = int(questionss[index][2])
            questionss[index][2] -= 1
            questionss[index][2] = str(questionss[index][2])
    convert_to_csv_file("question.csv", questionss)


def cut_out_for_edit(questions, ind_to_cut):
    # <!--id,submission_time,view_number,vote_number,title,message,image-->
    list_of_que = []
    for index, item in enumerate(questions):
        if item[0] == str(ind_to_cut):
            list_of_que.append(item[4])
            list_of_que.append(item[5])
    return list_of_que
