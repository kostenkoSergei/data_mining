from pymongo import MongoClient
from collections import deque
import numpy as np

db_client = MongoClient('mongodb://localhost:27017')


def get_from_mongodb(database: str, table: str, elements: dict, multiple=True, silent=True) -> list:
    db = db_client[database]
    collection = db[table]
    if multiple:
        products = collection.find(elements)
        docs = [_ for _ in products]
        if not silent:
            print(f'{len(docs)} documents were received from database "{database}" with parameters {elements}')
        return docs
    else:
        if not silent:
            print(f'One document was received from database "{database}" with parameters {elements}')
        return collection.find_one(elements)


def determine_friends(database: str, table_name: str, user: str):
    user_followers = get_from_mongodb(database, table_name, {'user_name': user})
    user_followings = get_from_mongodb(database, table_name, {'follow_name': user})
    user_friends = []
    for item_followings in user_followings:
        for item_followers in user_followers:
            if item_followings['user_name'] == item_followers['follow_name']:
                user_friends.append(item_followings['user_name'])
                break
    return user_friends


def build_hs_line(graph, users_list, target_users):
    start = users_list.index(target_users[0])
    finish = users_list.index(target_users[1])
    parent = [None for _ in range(len(graph))]
    is_visited = [False for _ in range(len(graph))]

    deq = deque([start])
    is_visited[start] = True

    while len(deq) > 0:
        current = deq.pop()
        if current == finish:
            break
        for i, vertex in enumerate(graph[current]):
            if vertex == 1 and not is_visited[i]:
                is_visited[i] = True
                parent[i] = current
                deq.appendleft(i)
    else:
        return f'User {target_users[0]} has no common friends with {target_users[1]}'

    cost = 0
    way = deque([users_list[finish]])
    i = finish

    while parent[i] != start:
        cost += 1
        way.appendleft(users_list[parent[i]])
        i = parent[i]

    cost += 1
    way.appendleft(users_list[start])

    return f'Shortest handshake chain {list(way)} has {cost} people in line'


def get_users_name_list(database: str, table: str):
    db = db_client[database]
    collection = db[table]
    return collection.distinct('user_name')


def create_graph_from_mongodb(database: str, table: str, users_list: list):
    graph = []
    for i in range(len(users_list)):
        friends = determine_friends(database, table, users_list[i])
        graph_line = []
        for j in range(len(users_list)):
            friend_flag = 1 if friends.count(users_list[j]) else 0
            graph_line.append(friend_flag)
        graph.append(graph_line)
    return np.array(graph)


if __name__ == '__main__':
    db = 'inst_parser'
    table = 'InstagramUserFollowItems'
    target_users = ['tbazadaykin', 'vetrov7872']
    users_list = get_users_name_list(db, table)
    graph = create_graph_from_mongodb(db, table, users_list)
    print(build_hs_line(graph, users_list, target_users))
