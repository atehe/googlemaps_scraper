import json, requests

url = "https://www.google.com/search?tbm=map&authuser=0&hl=en&gl=ng&pb=!4m12!1m3!1d89211.47237931563!2d-0.17497645!3d51.49769164999999!2m3!1f0!2f0!3f0!3m2!1i862!2i862!4f13.1!7i20!8i80!10b1!12m8!1m1!18b1!2m3!5m1!6e2!20e3!10b1!16b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m2!1s0t3oYpjtO82BlwSEr7EQ!7e81!24m70!1m22!13m8!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!18m12!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!15b1!17b1!20b1!21b1!2b1!5m5!2b1!3b1!5b1!6b1!7b1!10m1!8e3!14m1!3b1!17b1!20m2!1e3!1e6!24b1!25b1!26b1!29b1!30m1!2b1!36b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m2!1b1!3b1!65m5!3m4!1m3!1m2!1i224!2i298!71b1!72m4!1m2!3b1!5b1!4b1!89b1!26m4!2m3!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i458!2i862!1m6!1m2!1i812!2i0!2m2!1i862!2i862!1m6!1m2!1i0!2i0!2m2!1i862!2i20!1m6!1m2!1i0!2i842!2m2!1i862!2i862!34m18!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!37m1!1e81!42b1!46m1!1e10!47m0!49m5!3b1!6m1!1b1!7m1!1e3!50m26!1m21!2m7!1u3!4sOpen+now!5e1!9s0ahUKEwifzv2k3Kf5AhXVwoUKHaBpD_sQ_KkBCNsGKBY!10m2!3m1!1e1!2m7!1u2!4sTop+rated!5e1!9s0ahUKEwifzv2k3Kf5AhXVwoUKHaBpD_sQ_KkBCNwGKBc!10m2!2m1!1e1!3m1!1u3!3m1!1u2!4BIAE!2e2!3m2!1b1!3b1!59BQ2dBd0Fn!67m2!7b1!10b1!69i613&q=sports%20seller%20in%20london&tch=1&ech=5&psi=0t3oYpjtO82BlwSEr7EQ.1659428311670.1"
# nt(f"Parsing page {i}")
api_response = requests.get(url)

# clean api_response
try:
    response_text = api_response.text[:-6]
    response_dict = json.loads(response_text)
except:
    response_text = api_response.text[:-6]
    response_dict = json.loads(response_text)

search_response = response_dict.get("d", "" * 6)[5:]
search_json = json.loads(search_response)

datas = search_json[0][1]

with open("test3.json", "a") as file:
    json.dump(datas, file)

# with open("test2.json", "r") as file:
#     datas = json.load(file)


# for i, look in enumerate(datas[1][14]):
#     print(look)
#     # if "800-961" in str(look):
#     #     print(str(look))
print(len(datas))
for i, data in enumerate(datas):
    try:

        print(len(data))
        # if i == 0:
        # continue

        # print(len(list_))

        # print(data[14])

        store_name = data[14][11]
        tags_list = data[14][32]
        location_list = data[14][2]

        postal_code = location_list[-2].split()[-1]
        country = location_list[-1]
        print(country, postal_code)

        location = ", ".join(location_list) if location_list else None

        url = data[14][7][0] if data[14][7] else None
        if url:
            url = url.replace("/url?q=", "").strip()
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
    except:
        continue
    # print(len(data[14]))
# for i, value in enumerate(data[14]):
#     if "800-961" in str(value):
#         print(i)
#         print("hello")

# pi
