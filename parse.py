import json

with open("file4.json", "r") as json_file:
    datas = json.load(json_file)


# for i, look in enumerate(datas[1][14]):
#     print(look)
#     # if "800-961" in str(look):
#     #     print(str(look))
for i, data in enumerate(datas):
    print(len(data))
    if i == 0:
        continue

    #     print(len(list_))

    # print(data[14])

    store_name = data[14][11]
    tags_list = data[14][32]
    location_list = data[14][2]

    location = ", ".join(location_list) if location_list else None

    url = data[14][7][1] if data[14][7] else None
    num_reviews = data[14][4][3][1] if data[14][4] else None
    average_reviews = data[14][4][7] if data[14][4] else None
    features_list = data[14][13]

    features = ", ".join(features_list) if features_list else None

    region = data[14][14]

    tags = []
    if tags_list:
        for tag in tags_list:
            if tag[1]:
                tags.append(tag[1])

        tag = ", ".join(tags)
    else:
        tag = None

    phone_number = data[14][178][0][0] if data[14][178] else None

    try:

        price_range = data[14][4][10]
    except:
        price_range = None
    print(price_range)
    print(location)
    print(average_reviews)
    print(num_reviews)
    print(url)
    print(features)

    print(store_name)
    print(region)
    print(tag)
    print(phone_number)

    print()
    # print(len(data[14]))
    # for i, value in enumerate(data[14]):
    #     if "800-961" in str(value):
    #         print(i)
    #         print("hello")

    # pi
