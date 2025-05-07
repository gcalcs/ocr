from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import uuid

app = Flask(__name__)

# Configurar CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Permite todas as origens para testes

# Configuração do MongoDB Atlas
MONGO_URI = "mongodb+srv://jmafilho:mYpqZGQuuoleenCz@cluster0.ka0bb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['gestran_db']
index_collection = db['index_page']
modules_collection = db['modules_page']
expansion_collection = db['expansion_page']

# Gerar UUID
def generate_uuid():
    return str(uuid.uuid4())

# Função auxiliar para converter documentos
def convert_document(doc):
    doc['_id'] = str(doc['_id'])
    if 'subtasks' in doc:
        for subtask in doc['subtasks']:
            subtask['_id'] = str(subtask['_id'])
    return doc

# Endpoints para index_page
@app.route('/api/topics', methods=['GET'])
def get_topics():
    try:
        topics = [convert_document(topic) for topic in index_collection.find()]
        return jsonify({'index': {'topics': topics}})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar tópicos: {str(e)}'}), 500

@app.route('/api/topics/<topic_id>', methods=['PATCH'])
def update_topic_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        value = data.get('value')
        if not field_path or value is None:
            return jsonify({'error': 'field_path e value são obrigatórios'}), 400

        update = {'$set': {field_path: value}}
        result = index_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhum campo atualizado'}), 404
        return jsonify({'message': 'Campo atualizado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar campo: {str(e)}'}), 500

@app.route('/api/topics/<topic_id>/field', methods=['DELETE'])
def delete_topic_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        subtask_id = data.get('subtask_id')

        if field_path:
            update = {'$unset': {field_path: ''}}
            result = index_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhum campo excluído'}), 404
            return jsonify({'message': 'Campo excluído com sucesso'})
        elif subtask_id:
            update = {'$pull': {'subtasks': {'_id': subtask_id}}}
            result = index_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhuma subtarefa excluída'}), 404
            return jsonify({'message': 'Subtarefa excluída com sucesso'})
        else:
            return jsonify({'error': 'field_path ou subtask_id é obrigatório'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir: {str(e)}'}), 500

@app.route('/api/topics', methods=['POST'])
def add_topic():
    try:
        new_topic = request.json
        new_topic['_id'] = generate_uuid()
        result = index_collection.insert_one(new_topic)
        new_topic['_id'] = str(result.inserted_id)
        return jsonify({'inserted_id': new_topic['_id'], 'message': 'Tópico adicionado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar tópico: {str(e)}'}), 500

@app.route('/api/topics/<topic_id>/subtasks', methods=['POST'])
def add_subtask(topic_id):
    try:
        new_subtask = request.json
        new_subtask['_id'] = generate_uuid()
        update = {'$push': {'subtasks': new_subtask}}
        result = index_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhuma subtarefa adicionada'}), 404
        return jsonify({'message': 'Subtarefa adicionada com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar subtarefa: {str(e)}'}), 500

@app.route('/api/topics/reorder', methods=['PUT'])
def reorder_topics():
    try:
        topics = request.json
        index_collection.delete_many({})
        if topics:
            for topic in topics:
                topic['_id'] = ObjectId(topic['_id'])
                if 'subtasks' in topic:
                    for subtask in topic['subtasks']:
                        subtask['_id'] = subtask['_id']
            index_collection.insert_many(topics)
        return jsonify({'message': 'Tópicos reordenados com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao reordenar tópicos: {str(e)}'}), 500

@app.route('/api/topics/<topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    try:
        result = index_collection.delete_one({'_id': ObjectId(topic_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Nenhum tópico excluído'}), 404
        return jsonify({'message': 'Tópico excluído com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir tópico: {str(e)}'}), 500

# Endpoints para modules_page
@app.route('/api/modules', methods=['GET'])
def get_modules():
    try:
        topics = [convert_document(topic) for topic in modules_collection.find()]
        return jsonify({'modules': {'topics': topics}})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar módulos: {str(e)}'}), 500

@app.route('/api/modules/<topic_id>', methods=['PATCH'])
def update_module_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        value = data.get('value')
        if not field_path or value is None:
            return jsonify({'error': 'field_path e value são obrigatórios'}), 400

        update = {'$set': {field_path: value}}
        result = modules_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhum campo atualizado'}), 404
        return jsonify({'message': 'Campo atualizado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar campo: {str(e)}'}), 500

@app.route('/api/modules/<topic_id>/field', methods=['DELETE'])
def delete_module_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        subtask_id = data.get('subtask_id')

        if field_path:
            update = {'$unset': {field_path: ''}}
            result = modules_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhum campo excluído'}), 404
            return jsonify({'message': 'Campo excluído com sucesso'})
        elif subtask_id:
            update = {'$pull': {'subtasks': {'_id': subtask_id}}}
            result = modules_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhuma subtarefa excluída'}), 404
            return jsonify({'message': 'Subtarefa excluída com sucesso'})
        else:
            return jsonify({'error': 'field_path ou subtask_id é obrigatório'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir: {str(e)}'}), 500

@app.route('/api/modules', methods=['POST'])
def add_module():
    try:
        new_topic = request.json
        new_topic['_id'] = generate_uuid()
        result = modules_collection.insert_one(new_topic)
        new_topic['_id'] = str(result.inserted_id)
        return jsonify({'inserted_id': new_topic['_id'], 'message': 'Módulo adicionado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar módulo: {str(e)}'}), 500

@app.route('/api/modules/<topic_id>/subtasks', methods=['POST'])
def add_module_subtask(topic_id):
    try:
        new_subtask = request.json
        new_subtask['_id'] = generate_uuid()
        update = {'$push': {'subtasks': new_subtask}}
        result = modules_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhuma subtarefa adicionada'}), 404
        return jsonify({'message': 'Subtarefa adicionada com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar subtarefa: {str(e)}'}), 500

@app.route('/api/modules/reorder', methods=['PUT'])
def reorder_modules():
    try:
        topics = request.json
        modules_collection.delete_many({})
        if topics:
            for topic in topics:
                topic['_id'] = ObjectId(topic['_id'])
                if 'subtasks' in topic:
                    for subtask in topic['subtasks']:
                        subtask['_id'] = subtask['_id']
            modules_collection.insert_many(topics)
        return jsonify({'message': 'Módulos reordenados com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao reordenar módulos: {str(e)}'}), 500

@app.route('/api/modules/<topic_id>', methods=['DELETE'])
def delete_module(topic_id):
    try:
        result = modules_collection.delete_one({'_id': ObjectId(topic_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Nenhum módulo excluído'}), 404
        return jsonify({'message': 'Módulo excluído com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir módulo: {str(e)}'}), 500

# Endpoints para expansion_page
@app.route('/api/expansion', methods=['GET'])
def get_expansion():
    try:
        topics = [convert_document(topic) for topic in expansion_collection.find()]
        return jsonify({'expansion': {'topics': topics}})
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar expansão: {str(e)}'}), 500

@app.route('/api/expansion/<topic_id>', methods=['PATCH'])
def update_expansion_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        value = data.get('value')
        if not field_path or value is None:
            return jsonify({'error': 'field_path e value são obrigatórios'}), 400

        update = {'$set': {field_path: value}}
        result = expansion_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhum campo atualizado'}), 404
        return jsonify({'message': 'Campo atualizado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar campo: {str(e)}'}), 500

@app.route('/api/expansion/<topic_id>/field', methods=['DELETE'])
def delete_expansion_field(topic_id):
    try:
        data = request.json
        field_path = data.get('field_path')
        subtask_id = data.get('subtask_id')

        if field_path:
            update = {'$unset': {field_path: ''}}
            result = expansion_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhum campo excluído'}), 404
            return jsonify({'message': 'Campo excluído com sucesso'})
        elif subtask_id:
            update = {'$pull': {'subtasks': {'_id': subtask_id}}}
            result = expansion_collection.update_one({'_id': ObjectId(topic_id)}, update)
            if result.modified_count == 0:
                return jsonify({'error': 'Nenhuma subtarefa excluída'}), 404
            return jsonify({'message': 'Subtarefa excluída com sucesso'})
        else:
            return jsonify({'error': 'field_path ou subtask_id é obrigatório'}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir: {str(e)}'}), 500

@app.route('/api/expansion', methods=['POST'])
def add_expansion():
    try:
        new_topic = request.json
        new_topic['_id'] = generate_uuid()
        result = expansion_collection.insert_one(new_topic)
        new_topic['_id'] = str(result.inserted_id)
        return jsonify({'inserted_id': new_topic['_id'], 'message': 'Expansão adicionada com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar expansão: {str(e)}'}), 500

@app.route('/api/expansion/<topic_id>/subtasks', methods=['POST'])
def add_expansion_subtask(topic_id):
    try:
        new_subtask = request.json
        new_subtask['_id'] = generate_uuid()
        update = {'$push': {'subtasks': new_subtask}}
        result = expansion_collection.update_one({'_id': ObjectId(topic_id)}, update)
        if result.modified_count == 0:
            return jsonify({'error': 'Nenhuma subtarefa adicionada'}), 404
        return jsonify({'message': 'Subtarefa adicionada com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar subtarefa: {str(e)}'}), 500

@app.route('/api/expansion/reorder', methods=['PUT'])
def reorder_expansion():
    try:
        topics = request.json
        expansion_collection.delete_many({})
        if topics:
            for topic in topics:
                topic['_id'] = ObjectId(topic['_id'])
                if 'subtasks' in topic:
                    for subtask in topic['subtasks']:
                        subtask['_id'] = subtask['_id']
            expansion_collection.insert_many(topics)
        return jsonify({'message': 'Expansões reordenadas com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao reordenar expansões: {str(e)}'}), 500

@app.route('/api/expansion/<topic_id>', methods=['DELETE'])
def delete_expansion(topic_id):
    try:
        result = expansion_collection.delete_one({'_id': ObjectId(topic_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Nenhuma expansão excluída'}), 404
        return jsonify({'message': 'Expansão excluída com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao excluir expansão: {str(e)}'}), 500

# Configurar o diretório estático
app.static_folder = 'static'
app.static_url_path = '/static'

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')