from mutations import Mutation
from queries import Query
import strawberry

schema = strawberry.Schema(query=Query, mutation=Mutation)
