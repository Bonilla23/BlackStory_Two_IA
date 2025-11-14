# Rol

Eres un programador de Python especializado en videojuegos

# Contexto

Tienes que crear una aplicación completa de Black Stories donde dos IAs juegan entre sí.

# Objetivo

Crear un juego en Python donde dos modelos de IA juegan al juego Black Stories, con las siguientes características:

## Mecánica del juego
- **IA Narrador**: Conoce la historia completa y responde solo "sí", "no" o "no es relevante"
- **IA Detective**: Hace preguntas para descubrir qué pasó en la historia
- El detective tiene UNA oportunidad de dar la solución final. Si falla, pierde el juego
- No hay límite de preguntas hasta que el detective decida intentar resolver

## Generación de historias
- Las historias se generan automáticamente usando una IA antes de empezar
- El usuario puede seleccionar la dificultad: fácil, media o difícil
- La generación es completamente automática sin intervención manual

## Interfaz de usuario
- Mostrar cada pregunta del detective
- Mostrar la respuesta del narrador
- El usuario debe presionar ENTER para continuar a la siguiente pregunta
- Interfaz simple: solo pregunta y respuesta, sin información adicional

## Validación
- La IA narrador evalúa automáticamente si la solución final es correcta
- Muestra si el detective ganó o perdió al final

## Pantalla final
Al terminar el juego (gane o pierda el detective), mostrar:
- La historia completa original que se generó al inicio
- Explicación detallada de por qué el detective ganó o perdió (qué elementos acertó, qué falló, qué le faltó)

## Manejo de errores
- Si hay error de conexión con las APIs, preguntar al usuario si quiere reintentar
- No incluir modo debug o verbose

# Ejemplos de uso

```bash
uv run main.py -narrador gemini:gemini-flash -detective ollama:llama2
uv run main.py -narrador gemini:gemini-pro -detective gemini:gemini-flash -dificultad dificil
```

# Requisitos técnicos

## Estructura del proyecto
- **main.py**: Punto de entrada
- **pyproject.toml**: Configuración del proyecto para uv
- **README.md**: Documentación completa
- **.env**: API keys (no subir a git)
- **.env.example**: Ejemplo de configuración de API keys
- **.gitignore**: Incluir .env y archivos típicos de Python
- **.claudeignore**: Incluir .env
- **src/**: Módulos organizados por responsabilidad

## Arquitectura de código
- Métodos y archivos con responsabilidades limitadas y bien definidas
- Nombres descriptivos para archivos, clases y métodos
- Comentarios sencillos y descriptivos
- Sin librerías externas (solo stdlib de Python)
- Usar solo `uv` para gestión del proyecto

## Configuración
- Argumentos CLI: `-narrador provider:modelo -detective provider:modelo -dificultad facil|media|dificil`
- API keys en archivo .env:
  - `GEMINI_API_KEY=tu_key_aqui`
  - `OLLAMA_API_URL=http://localhost:11434` (si aplica)

## Providers soportados
- **Gemini**: Google AI Studio
- **Ollama**: Local LLM server

# Entregables

1. Código fuente completo con todos los archivos
2. README.md con instrucciones de instalación y uso
3. Mensaje de commit sugerido para el proyecto
4. Todos los archivos de configuración (.env.example, .gitignore, .claudeignore, pyproject.toml)

# Calidad de código

- Código limpio y mantenible
- Sin dependencias externas
- Manejo robusto de errores
- Arquitectura modular y escalable