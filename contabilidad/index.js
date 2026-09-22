const express = require('express');
const mongoose = require('mongoose');
const app = express();
const PORT = 3000;

app.use(express.json());

// Conexión a MongoDB
mongoose.connect('TU_URI_DE_CONEXION', { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Conectado a MongoDB'))
  .catch(err => console.error('Error de conexión:', err));

// Definir esquema y modelo
const productoSchema = new mongoose.Schema({
  nombre: String,
  precio: Number
});

const Producto = mongoose.model('Producto', productoSchema);

// Endpoints
app.get('/', (req, res) => {
  res.send('¡API conectada a MongoDB!');
});

// Obtener todos los productos
app.get('/productos', async (req, res) => {
  const productos = await Producto.find();
  res.json(productos);
});

// Crear producto nuevo
app.post('/productos', async (req, res) => {
  const nuevoProducto = new Producto({
    nombre: req.body.nombre,
    precio: req.body.precio
  });
  await nuevoProducto.save();
  res.status(201).json(nuevoProducto);
});

app.listen(PORT, () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
