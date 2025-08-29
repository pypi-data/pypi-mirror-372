def has_memo_been_posted(memo):
    with open('posted_memos.txt', 'r') as file:
        posted_memos = file.read().splitlines()
    return memo in posted_memos

def record_posted_memo(memo):
    with open('posted_memos.txt', 'a') as file:
        file.write(memo + '\n')

def delete_file_content(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)
