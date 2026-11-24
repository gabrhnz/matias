# MatiLab

Práctica de matemáticas para 3.º a 6.º grado. El niño entra, elige un módulo, resuelve ejercicios y ve en el momento si acertó. El sitio está en https://matiaslab.vercel.app.

Somos tres. Gabriel hizo el desarrollo. María Belinda hizo el diseño y el frontend. Gure hizo las pruebas, encontró los errores y dejó las soluciones.

## Qué hace

Hay cuatro módulos y 32 lecciones. Cada lección tiene 4 ejercicios: 128 en total.

| Módulo | Qué practica |
| --- | --- |
| Aritmética | Sumas, restas, tablas, multiplicación, división y problemas |
| Fracciones | Partes de un entero, comparar, sumar, restar y números mixtos |
| Geometría | Figuras, perímetro, área, ángulos y volumen |
| Razonamiento lógico | Patrones, verdadero o falso, clasificar y deducir |

El representante crea la cuenta con su nombre y su correo. El código de entrada llega a ese correo. Después se guarda el nombre del estudiante, el grado y la escuela.

El estudiante solo practica las lecciones de su grado. Las demás aparecen bloqueadas. Si quiere verlas, elige “Ver otros grados”. Eso no cambia su grado.

Arriba se ve una llama con la racha: cuenta un día de Venezuela si el estudiante respondió al menos un ejercicio.

## Cómo lo hace

1. El navegador pide una página. El servidor arma el HTML con los datos de la lección.
2. La respuesta correcta no viaja al navegador. El niño envía su respuesta y el servidor dice si está bien.
3. Si se equivoca, el texto dice que esa no era y pasa al siguiente ejercicio. Si acierta, muestra la explicación y espera a que pulse Siguiente.
4. El orden no es siempre el mismo. Empieza por un ejercicio normal. Dos errores seguidos bajan a uno más fácil. Tres aciertos seguidos cierran con uno más difícil.
5. El progreso y la racha se guardan en la base de datos, ligados a la cuenta.

## Stack

| Pieza | Para qué |
| --- | --- |
| Python y FastAPI | El servidor y las rutas |
| Jinja | Las páginas HTML |
| HTML, CSS y JavaScript | Lo que ve el niño |
| Supabase | Cuentas, código al correo y progreso |
| Vercel | Publicar el sitio. Cada push de la rama `cursor/matilab-plataforma` lo actualiza |
| pytest | Las pruebas automáticas |

El navegador no habla con la base de datos. Solo habla con MatiLab. El servidor es el que guarda y lee.

---

## Gabriel — desarrollo

Gabriel armó el programa que hace funcionar la plataforma.

El contenido vive en el servidor: 4 módulos, 32 lecciones y 128 ejercicios. Ahí está el enunciado, la respuesta y la explicación. El navegador nunca recibe la respuesta antes de tiempo.

Las páginas salen de Python. Inicio, módulo, lección, Mi progreso, Conócenos y la entrada son rutas del servidor. Cuando el niño responde, una ruta comprueba el ejercicio, guarda el avance y decide cuál sigue.

El ingreso es un código de 6 números al correo del representante. Supabase envía el correo. MatiLab comprueba el código y abre una sesión. En el registro quedan el representante, el estudiante, el grado y la escuela.

El grado de la cuenta decide qué lecciones están abiertas. Entrar a una de otro grado, o responderla, queda bloqueado hasta que se pide el repaso.

La racha mira el día en Venezuela. El mismo día no sube. El día siguiente suma uno. Si se salta un día, vuelve a uno.

Si la base de datos no está configurada, la práctica igual corre: el código se muestra en pantalla y el progreso queda en memoria. En el sitio publicado sí usa Supabase.

El proyecto se publica en Vercel. La rama de producción es `cursor/matilab-plataforma`.

## María Belinda — diseño y frontend

María Belinda definió cómo se ve y cómo se usa.

La página es clara y cálida: fondo suave, títulos en una letra con serifa, texto en una letra sencilla, botones en forma de pastilla y un solo verde para la acción principal. Los cuatro módulos se distinguen con tintes pálidos: durazno, azul, verde y lila.

Fracciones y geometría no son solo texto. El navegador dibuja la figura: tortas, barras, figuras, ángulos y prismas. En las opciones, cada fracción se puede contar: las partes se marcan y una fracción mayor que uno se ve como círculos enteros más el resto.

En el teléfono el menú se parte en dos filas, las tarjetas se apilan y los botones ocupan el ancho. En la computadora se mantiene la misma estética, en una sola fila.

El menú muestra Módulos siempre. Mi progreso solo aparece con la sesión iniciada. Al lado está Conócenos, con el equipo, el aula y el campus en fotos pequeñas, texto e imagen intercalados.

El pie dice: MatiLab · Hecho con ♥ desde Venezuela.

## Gure — pruebas, errores y soluciones

Gure revisó que lo que se explica también ocurra en la pantalla, y dejó escrito lo que fallaba y cómo se corrigió.

Las pruebas automáticas cubren el repertorio, que la explicación no salga antes de responder, el acierto y el error, las fracciones equivalentes, las figuras, el registro, el grado bloqueado, la racha y el cambio de dificultad. Se corren con `pytest`.

Errores que aparecieron y cómo quedaron:

| Qué pasaba | Qué se hizo |
| --- | --- |
| El correo de registro llegaba como un enlace y abría localhost | El correo ahora muestra el código de 6 números. El sitio publicado ya no manda al computador local |
| Las fracciones de las opciones no se podían contar: el trazo tapaba los cortes | El trazo se ajusta al tamaño y cada parte queda marcada. 8/3 se ve como dos enteros y un tercio |
| En el teléfono el menú y las tarjetas se salían del diseño de escritorio | El menú pasa a dos filas y las tarjetas se apilan, sin cambiar la estética |
| En Conócenos la foto quedaba con un hueco blanco grande debajo | La imagen queda centrada junto al texto y el pie de foto también va centrado |
| Una lección de otro grado se podía abrir directo | Sin sesión de repaso, la página y la respuesta quedan bloqueadas |

---

## Orden para explicarlo

1. Los tres, en una frase: MatiLab es práctica de matemáticas de 3.º a 6.º, con cuenta del representante y progreso del estudiante.
2. Gabriel: cómo el servidor guarda el contenido, corrige, adapta el ejercicio y publica el sitio.
3. María Belinda: cómo se ve, cómo se dibujan las fracciones y cómo cambia en el teléfono.
4. Gure: qué se probó, qué falló y qué solución quedó.
