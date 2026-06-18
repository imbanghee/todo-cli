def add_task(tasks, task_name):
    tasks.append(task_name)
    return tasks


def format_task(index, task_name):
    return f"{index}. {task_name}"


def main():
    tasks = []
    add_task(tasks, '장보기')
    add_task(tasks, '운동하기')
    add_task(tasks, '독서하기')

    for i, task in enumerate(tasks, start=1):
        print(format_task(i, task))


if __name__ == '__main__':
    main()
