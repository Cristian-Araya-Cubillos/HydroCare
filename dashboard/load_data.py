# https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/mongodb_atlas

#from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
import params
from langchain.document_loaders import DirectoryLoader

# Step 1: Load
#loaders = [
 #WebBaseLoader("https://en.wikipedia.org/wiki/AT%26T"),
 #PyPDFLoader("datosA.pdf"),
 #PyPDFLoader("crisishidrica_removed.pdf")
 #WebBaseLoader("https://en.wikipedia.org/wiki/Bank_of_America")
#]

loaders = DirectoryLoader('data', glob="./*.pdf", loader_cls=PyPDFLoader)
papers = loaders.load()
# Step 2: Transform (Split)
text_splitter = RecursiveCharacterTextSplitter (chunk_size=1000, chunk_overlap=5)
docs = text_splitter.split_documents(papers)
data = []
#for loader in loaders:
#    data.extend(loader.load())
print('Split into ' + str(len(docs)) + ' docs')

# Step 3: Embed
# https://api.python.langchain.com/en/latest/embeddings/langchain.embeddings.openai.OpenAIEmbeddings.html
embeddings = OpenAIEmbeddings(openai_api_key=params.openai_api_key)

# Step 4: Store
# Initialize MongoDB python client
client = MongoClient(params.mongodb_conn_string)
collection = client[params.db_name][params.collection_name]

# Reset w/out deleting the Search Index 
collection.delete_many({})

# Insert the documents in MongoDB Atlas with their embedding
# https://github.com/hwchase17/langchain/blob/master/langchain/vectorstores/mongodb_atlas.py
docsearch = MongoDBAtlasVectorSearch.from_documents(
    docs, embeddings, collection=collection, index_name=params.index_name
)
