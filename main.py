from flask import Flask, request, jsonify
from datetime import datetime
import requests

app = Flask(__name__)

HEADERS = {
  "Content-Type": "application/json",
  "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3MDQyMDIzOTMsImp0aSI6IjAyZmI0MGFmLWYwNGQtNGNjMi05Yjc4LWJkZmQ5YzhhZWM4NCIsInN1YiI6MzA0MTY1MTY2LCJ1c2VyIjp7ImlkIjozMDQxNjUxNjYsImVtYWlsIjoiZGVzYWZpb2ludGVncmFjYW9AcHJvZmVjdHVtLmNvbS5iciIsImFwcGxpY2F0aW9uIjozMDAzMDU3MDEsInNjb3BlcyI6W119LCJpbnRlcmZhY2VfdXVpZCI6bnVsbH0.NDCy-EvEyaQpct5lEeaXRdCCWCuU4K-DRggf2wdZIsVMo8tIwk0kY7bPVPnngajjULE_hF-O0rqqydkyzJiNBA"
}
PIPEFY_URL = "https://api.pipefy.com/graphql"
PIPE_ID = 303843596
ACCOUNT_ID = 304165166
INITIAL_PHASE = 323403002
ORGANIZATION_ID = 301236187

TABLE_MARI = "yVETHzHv"

@app.route("/")
def home():
  return "Desafio - Vaga Profectum 2024.1"

@app.route("/api/card/create", methods=["POST"])
def create_card(): 
  data = request.json
  title = data.get('title')
  name = data.get('name')
  cpf = data.get('cpf')
  phone = data.get('phone')
  genre = data.get('genre')
  hobbie = data.get('hobbie')
  city = data.get('city')
  label = data.get('label')

  print("===================================================")
  print("Datas received >> ", data)  
  print("===================================================")

  card_data_formated = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

  card = """
      mutation {
          createCard(input: {
              clientMutationId: "%s",
              pipe_id: "%s",
              title: "%s",
              due_date: "%s",
              phase_id: "%s",
              assignee_ids: [
                "%s",
              ],
              fields_attributes: [
                {field_id: "nome", field_value: "%s"},
                {field_id: "cpf", field_value: "%s"}
                {field_id: "telefone", field_value: "%s"}
                {field_id: "data", field_value: "%s"}
                {field_id: "sexo", field_value: "%s"}
                {field_id: "hobbies", field_value: "%s"}
                {field_id: "cidade", field_value: "%s"}
              ],
              label_ids: [
                "%s"
              ]
          }) {
              card {
                  title
                  id
              }
          }
      }
  """ % (ACCOUNT_ID, PIPE_ID, title, card_data_formated, INITIAL_PHASE, ACCOUNT_ID, name, 
          cpf, phone, card_data_formated, genre, hobbie, city, label);

  response = requests.post(PIPEFY_URL, json={'query': card}, headers=HEADERS)

  if response.status_code != 200 or 'errors' in response.json():
    return jsonify({'Error >> ': response.json()}), 500
  else:
    card = response.json()
    return jsonify({'Message': 'Card created successfully', 'card': card})

@app.route("/api/card/delete", methods=["DELETE"])
def delete_card(): 
  data = request.json

  card_id = data.get('id')

  info = """
    mutation {
      deleteCard(input: {id: "%s"}) {
        success
      }
    }
  """ % (card_id)
  
  response = requests.post(PIPEFY_URL, json={'query': info}, headers=HEADERS)

  if response.status_code != 200 or 'errors' in response.json():
    return jsonify({'problem >> ': response.json()}), 500
  else:
    return jsonify({'Deleted': 'The card was deleted'})


@app.route("/api/card/update-phase", methods=["PUT"])
def update_phase():
  data = request.json
  card_id = data.get('id')

  info = """
    query {
      card(id: "%s") {
        done
          current_phase {
            next_phase_ids
            previous_phase_ids
            description
          }
      }
    }
  """ % (card_id)

  response = requests.post(PIPEFY_URL, json={'query': info}, headers=HEADERS)
  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error': response.json()}), 500
  
  response_data = response.json()
  
  card_data = response_data.get('data', {}).get('card', {})
  done = card_data.get('done')

  current_phase = card_data.get('current_phase', {})

  next_phase_ids = current_phase.get('next_phase_ids', [])
  previous_phase_ids = current_phase.get('previous_phase_ids', [])
  description = current_phase.get('description')

  if isinstance(next_phase_ids, set):
      next_phase_ids = list(next_phase_ids)
  if isinstance(previous_phase_ids, set):
      previous_phase_ids = list(previous_phase_ids)

  if (done == True):
    return jsonify({"Your card is already at the final phase!! We can't update anymore.": { 
      "done": done,
      "description": description
      }
    })

  print("===================================================")
  print("Next phases >> ", next_phase_ids)
  print("===================================================")
  
  next_phase = next_phase_ids[0]
  update_phase = """
    mutation {
      moveCardToPhase(input: { 
        clientMutationId: "%s"
        card_id: "%s" 
        destination_phase_id: "%s"
      }) {
        card {
          title
          current_phase {
            name
          }
        }
      }
    }
  """ % (ACCOUNT_ID, card_id, next_phase)

  response = requests.post(PIPEFY_URL, json={'query': update_phase}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  response_moved = response.json();
  phase = response_moved.get('data', {}).get('moveCardToPhase', {}).get('card', {}).get('current_phase', {})

  return jsonify({"Current Phase Info": phase, "Phase": "The phase was updated!"})

@app.route("/api/card/allcards", methods=["GET"])
def get_cards():
  info = """
    query {
      allCards(pipeId: "%s") {
        edges {
          node {
            id
            title
            labels {
              name
            },
            current_phase {
              name
              description
            }
          }
        }
      }
    }
  """ % (PIPE_ID)
  
  response = requests.post(PIPEFY_URL, json={'query': info}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  response_data = response.json()
  return jsonify({"All cards": response_data})

@app.route("/api/label/create-label", methods=["POST"])
def create_label():
  data = request.json

  pink = "#ffa6ff"
  name = data.get('name')
  
  label = """
    mutation {
      createLabel(input: { 
        clientMutationId: "%s"
        color: "%s"
        name: "%s"
        pipe_id: "%s"
        table_id: "%s"
      }) {
        label {
          color
          id
          name
        }
      }
    }
  """ % (ACCOUNT_ID, pink, name, PIPE_ID, TABLE_MARI)

  response = requests.post(PIPEFY_URL, json={'query': label}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500
  
  response_data = response.json()
  
  return jsonify({"Your label was created succesfully!": response_data})

@app.route("/api/label/allLabels", methods=["GET"])
def get_labels():
  label = """
    query {
      pipe(id: "%s") {
        labels {
          color
          id
          name
        }
      }
    }
  """ % (PIPE_ID)

  response = requests.post(PIPEFY_URL, json={'query': label}, headers=HEADERS)
  
  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  response_data = response.json()

  return jsonify({"Response": response_data})

@app.route("/api/label/label-delete", methods=["DELETE"])
def delete_label():
  data = request.json
  id = data.get('id')

  label = """
    mutation {
      deleteLabel(input: {id: "%s"}) {
        clientMutationId
        success
      }
    }
  """ % (id)

  response = requests.post(PIPEFY_URL, json={'query': label}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  return jsonify({"Res": "Your LABEL was deleted!"})

@app.route("/api/table/create-table", methods=["POST"])
def create_table():
  data = request.json
  name = data.get('name')

  table = """
    mutation {
      createTable(input: {organization_id: "%s", name: "%s" }) {
        clientMutationId
        table {
          id
        }
      }
    }
  """ % (ORGANIZATION_ID, name)
  
  response = requests.post(PIPEFY_URL, json={'query': table}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500
  
  return jsonify({"Res": "Your table was created succesfully!"})

@app.route("/api/table/allTables", methods=["GET"])
def get_tables(): 
  table = """
    query {
      organization(id:"%s") {
        tables{
          edges{
            node{
              id
              name
            }
          }
        }
      }
    }
  """ % (ORGANIZATION_ID)

  response = requests.post(PIPEFY_URL, json={'query': table}, headers=HEADERS)
  
  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  response_data = response.json()

  return jsonify({"Response": response_data})

@app.route("/api/table/table-delete", methods=["DELETE"])
def delete_table():
  data = request.json
  id = data.get('id')

  table = """
    mutation {
      deleteTable(input: {id: "%s"}) {
        clientMutationId
        success
      }
    }
  """ % (id)

  response = requests.post(PIPEFY_URL, json={'query': table}, headers=HEADERS)

  if (response.status_code != 200 or 'errors' in response.json()):
    return jsonify({'error ': response.json()}), 500

  return jsonify({"Res": "Your table was deleted!"})

if __name__ == "__main__":
  app.run(debug=True)