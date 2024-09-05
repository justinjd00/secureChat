from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI()

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8012)

# Info:
# Starte die App und gehe auf http://127.0.0.1:8000/graphql (passe jeweils Host und port von oben an), dann kann du die subscription und 
# mutation jeweils angeben (subscription ist sozusagen ein listener der live wartet dass nachrichten versendet werden und mutation für nachricht eingabe
# subscription {
#    messageFeed {
#    id
#    content
#    sender
# }
#}
#mutation {
#    sendMessage(content: "Was geht yo!", sender: "Alice") {
#    id
#    content
#    sender
# }
#}
