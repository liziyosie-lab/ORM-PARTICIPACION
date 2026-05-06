from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# --- Configuración de la Aplicación Flask ---
app = Flask(__name__)
# Configuración de la base de datos (SQLite en este caso)
# 'sqlite:///nombre_de_tu_base.db' -> creará un archivo .db en tu carpeta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recomendado para deshabilitar eventos de seguimiento

# Inicializa Flask-SQLAlchemy
db = SQLAlchemy(app)

# --- Definición del Modelo Product con Flask-SQLAlchemy ---
# En Flask-SQLAlchemy, los modelos heredan de db.Model (que ya incluye DeclarativeBase)
class Product(db.Model):
    __tablename__ = 'products' # Nombre de la tabla en la base de datos

    # Columnas según los requisitos:
    # Mapped y mapped_column son la forma moderna y recomendada en SQLAlchemy 2.0+
    id: Mapped[int] = mapped_column(Integer, primary_key=True) # Clave primaria, autoincrementable
    name: Mapped[str] = mapped_column(String(100), nullable=False) # String con longitud, no nulo
    price: Mapped[float] = mapped_column(Float, nullable=False)   # Float, no nulo
    stock: Mapped[int] = mapped_column(Integer, default=0)        # Integer, valor por defecto 0

    # Método para una representación amigable del objeto Product (útil para depuración)
    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'

    # Método para serializar el objeto a un diccionario (útil para respuestas JSON)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock
        }

# --- Rutas de la API (Operaciones CRUD) ---

@app.route('/')
def home():
    return '¡Bienvenido a la API de Productos con Flask y Flask-SQLAlchemy!'

# CREAR un nuevo producto (POST)
@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json() # Obtiene los datos JSON enviados en la petición
    if not data or not all(key in data for key in ['name', 'price']):
        return jsonify({'message': 'Datos incompletos para crear producto (se requiere name y price)'}), 400

    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock=data.get('stock', 0) # Si 'stock' no se proporciona, usa el valor por defecto 0
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201 # Retorna el producto creado con código 201 (Created)

# OBTENER todos los productos (GET)
@app.route('/products', methods=['GET'])
def get_products():
    products = db.session.execute(db.select(Product)).scalars().all() # SQLAlchemy 2.0 query
    return jsonify([product.to_dict() for product in products])

# OBTENER un producto por ID (GET)
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # db.get_or_404 es una función útil de Flask-SQLAlchemy
    product = db.session.get(Product, product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({'message': 'Producto no encontrado'}), 404

# ACTUALIZAR un producto existente (PUT/PATCH)
@app.route('/products/<int:product_id>', methods=['PUT', 'PATCH'])
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No se proporcionaron datos para actualizar'}), 400

    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']

    db.session.commit()
    return jsonify(product.to_dict())

# ELIMINAR un producto (DELETE)
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado exitosamente'}), 200

# --- Bloque Principal de Ejecución ---
if __name__ == '__main__':
    # Esto asegura que las tablas se creen la primera vez que ejecutas la aplicación
    # o si no existen.
    with app.app_context():
        db.create_all()
    
    # Inicia el servidor de desarrollo de Flask
    # debug=True permite la recarga automática y muestra errores detallados
    app.run(debug=True)