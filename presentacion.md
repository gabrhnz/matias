# MatiLab

Práctica de matemáticas para 3.º a 6.º grado.

- Sitio: https://matiaslab.vercel.app
- Código: https://github.com/gabrhnz/matias

[1. Para qué sirve](#1-para-qué-sirve) · [2. Cómo funciona](#2-cómo-funciona) · [3. Con qué está hecha](#3-con-qué-está-hecha) · [4. Quién hizo qué](#4-quién-hizo-qué) · [Textos para cada quien](#textos-para-enviar)

Somos cuatro. Gabriel hizo el desarrollo. María Belinda hizo el diseño y el frontend. Carol hizo el contenido y la pedagogía. Gure hizo las pruebas, encontró los errores y dejó las soluciones. El proyecto nace en la Universidad Nacional de las Ciencias: las bases escolares sostienen lo que después se estudia, y MatiLab pone esas bases a practicar.

## 1. Para qué sirve

El niño practica, no solo lee. Entra, elige un módulo, resuelve ejercicios y ve en el momento si acertó. Cada lección trae una idea corta, un ejemplo y una pista. La pista empuja sin dar la respuesta. Carol escribió ese texto para 3.º a 6.º: frases cortas y palabras de todos los días.

Hay cuatro módulos, 32 lecciones y 128 ejercicios. Cada lección tiene 4 ejercicios.

| Módulo | Qué practica |
| --- | --- |
| Aritmética | Sumas, restas, tablas, multiplicación, división y problemas |
| Fracciones | Partes de un entero, comparar, sumar, restar y números mixtos |
| Geometría | Figuras, perímetro, área, ángulos y volumen |
| Razonamiento lógico | Patrones, verdadero o falso, clasificar y deducir |

La cuenta la crea el representante: su nombre, su correo, y después el nombre del estudiante, el grado y la escuela. El estudiante practica las lecciones de su grado. Las de otros grados se ven, pero bloqueadas, hasta que se pide verlas. Eso no cambia el grado de la cuenta.

Una lección se aprueba con al menos 75 sobre 100. El módulo queda aprobado cuando cada lección de ese grado llega a ese puntaje. Arriba, una llama marca la racha: un día de Venezuela cuenta si el estudiante respondió al menos un ejercicio.

Quien todavía no tiene cuenta puede empezar igual. «Empezar a practicar» abre tres preguntas. Al terminar, el botón lleva al registro.

## 2. Cómo funciona

El navegador pide una página y el servidor arma el HTML. La respuesta correcta no viaja al navegador. El niño envía lo que eligió y el servidor dice si está bien.

1. En una lección se empieza por un ejercicio normal. Dos errores seguidos bajan a uno más fácil. Tres aciertos seguidos cierran con uno más difícil. Así se recorren los cuatro.
2. Al elegir o escribir, la pantalla se queda en el resultado: «Correcto» o «Incorrecto», con la explicación. No avanza sola. El niño pulsa «Seguir».
3. Al terminar los cuatro, el puntaje es aciertos sobre 100. Tres de cuatro son 75 sobre 100. Con 75 o más, la lección queda aprobada y el botón sigue a la siguiente. Por debajo, el botón es «Intentar otra vez».
4. En el módulo se lee la regla y el avance: «N de M aprobadas», o «Aprobado» cuando todas llegan a 75. El círculo verde solo aparece en las aprobadas.
5. El progreso y la racha se guardan con la cuenta. Reintentar una lección solo puede subir el puntaje guardado, no bajarlo.
6. La racha mira el día en Venezuela. El mismo día no sube. El día siguiente suma uno. Si se salta un día, vuelve a uno.
7. Sin sesión, una lección de otro grado no se abre ni se responde. Con «Ver otros grados» se puede repasar, y el grado de la cuenta sigue igual.

Las figuras no son una imagen fija. El navegador las dibuja: fracciones, barras, figuras, ángulos y prismas. En las opciones, cada fracción se puede contar. Una mayor que uno se ve como círculos enteros más el resto.

## 3. Con qué está hecha

El navegador no habla con la base de datos. Solo habla con MatiLab. El servidor guarda y lee.

| Pieza | Para qué |
| --- | --- |
| Python y FastAPI | El servidor, las páginas y las rutas que corrigen |
| Jinja | El HTML de inicio, módulo, lección, progreso, Conócenos, prueba y registro |
| HTML, CSS y JavaScript | Lo que ve y pulsa el niño. Sin otro marco de interfaz |
| Supabase | La cuenta, el código de 8 dígitos al correo y el progreso |
| Vercel | Publica el sitio. Cada push de `cursor/matilab-plataforma` lo actualiza |
| pytest | Las pruebas automáticas del repertorio, el puntaje y el bloqueo por grado |

El contenido vive en el servidor: enunciado, respuesta, explicación, idea y pista. Si Supabase no está configurado, la práctica igual corre: el código se muestra en pantalla y el progreso queda en memoria. En https://matiaslab.vercel.app sí usa Supabase. La clave de servicio no sale al navegador.

## 4. Quién hizo qué

**Gabriel — desarrollo.** Armó el programa. Las 32 lecciones y los 128 ejercicios están en el servidor, y la ruta de comprobar decide si la respuesta vale, guarda el avance y elige el siguiente ejercicio. El ingreso es el código al correo del representante. El grado abre sus lecciones. El umbral de 75 sobre 100 y la prueba de tres preguntas antes del registro también viven ahí. El sitio se publica en Vercel.

**María Belinda — diseño y frontend.** Definió cómo se ve y cómo se usa: fondo cálido, títulos con serifa, texto sencillo, botones en pastilla y un solo verde para la acción principal. Los cuatro módulos se distinguen con tintes pálidos. En el teléfono el menú se parte y las tarjetas se apilan. En la computadora todo queda en una fila. Conócenos muestra al equipo, el aula y el campus. El pie dice: MatiLab · Hecho con ♥ desde Venezuela.

**Carol — contenido y pedagogía.** Definió qué practica cada módulo y cómo se lo dice a un niño de 3.º a 6.º. Cada lección tiene una idea, un ejemplo y una pista: la pista orienta y no regala la respuesta. El 75 sobre 100 es la meta de la lección, y el módulo solo se aprueba cuando todas las de ese grado llegan ahí. Antes de crear la cuenta, tres preguntas dejan probar la práctica.

**Gure — pruebas, errores y soluciones.** Revisó que lo explicado ocurra en la pantalla. `pytest` cubre el repertorio, que la explicación no salga antes de responder, el acierto y el error, las fracciones, las figuras, el registro, el grado bloqueado, la racha, el cambio de dificultad y que 75 sobre 100 apruebe la lección.

| Qué pasaba | Qué se hizo |
| --- | --- |
| El correo de registro llegaba como un enlace y abría localhost | El correo muestra el código de 8 dígitos que manda Supabase |
| Las fracciones de las opciones no se podían contar | El trazo se ajusta y cada parte queda marcada |
| En el teléfono el menú y las tarjetas se salían | El menú pasa a dos filas y las tarjetas se apilan |
| En Conócenos la foto dejaba un hueco blanco | La imagen y el pie de foto quedan centrados junto al texto |
| Una lección de otro grado se podía abrir directo | Sin repaso, la página y la respuesta quedan bloqueadas |
| Al responder, la lección avanzaba sola y el puntaje salía como 1 de 4 | El resultado se queda hasta pulsar Seguir, y el puntaje es N sobre 100 |

## Textos para enviar

Cada quien explica su parte. Estos textos se pueden reenviar tal cual.

### Gabriel

Tu parte es el desarrollo: cómo está armado para que la práctica funcione de verdad. El sitio es https://matiaslab.vercel.app. No describas los colores ni leas las ideas de las lecciones: eso lo explican María Belinda y Carol. Tú explicas qué decide el servidor y por qué el niño no puede saltarse la regla.

Qué tienes que dejar claro: la página que ve el niño no trae la respuesta, no decide si aprobó y no guarda nada por su cuenta. Todo eso lo hace el servidor.

1. Qué es el programa. MatiLab es un servidor escrito en Python, con FastAPI. Cuando el niño abre inicio, un módulo, una lección, Mi progreso, Conócenos, la prueba o el registro, el servidor arma esa página. El contenido no está suelto en el navegador: 4 módulos, 32 lecciones y 128 ejercicios viven en el servidor, cada uno con su enunciado, su respuesta, su explicación, su idea y su pista. El sitio publicado está en Vercel. Cada vez que se sube la rama cursor/matilab-plataforma, el sitio se actualiza. Los dibujos y la interacción corren en el navegador. La corrección, no.

2. La respuesta no viaja. La página de la lección manda el enunciado, las opciones y la pista. No manda cuál opción es la buena ni el número que hay que escribir. El niño elige o escribe, y eso se envía al servidor. El servidor compara, ignora mayúsculas y espacios de más, y contesta dos cosas: si estuvo bien y la explicación. La explicación sale después de responder, nunca antes. Por eso abrir la página y mirar «el código de la página» no revela el resultado. La pista sí viaja, porque es una ayuda, y está escrita para no decir el número final.

3. El orden de los cuatro ejercicios lo decide el servidor, no una lista fija. En cada lección hay dos fáciles, uno normal y uno difícil. Se abre por el normal. El navegador le cuenta al servidor cuáles ya salieron y si estuvieron bien o mal. Dos errores seguidos: el siguiente es el más fácil que todavía no salió. Tres aciertos seguidos: el siguiente es el más difícil que todavía no salió. En cualquier otro caso, uno que no sea más difícil que el último. Cuando ya salieron los cuatro, el servidor dice que no hay siguiente. La pantalla no avanza sola: muestra Correcto o Incorrecto y espera a que el niño pulse Seguir. Seguir solo muestra el ejercicio que el servidor ya eligió.

4. Cómo se calcula el 75. Cada ejercicio vale lo mismo. El puntaje es los aciertos partidos entre 4, por 100, redondeado. Uno bien es 25. Dos son 50. Tres son 75. Cuatro son 100. La lección queda aprobada solo si recorrió los cuatro y el puntaje es 75 o más. Recorrerlos y aprobarlos son dos cosas distintas: se pueden responder los cuatro mal, la lección está terminada y no está aprobada. El módulo se aprueba cuando cada lección del grado de ese estudiante está aprobada. No es un promedio. Una en 50 deja el módulo en «3 de 4 aprobadas». Si no llegó a 75, el botón principal vuelve a la misma lección. Si llegó, sigue a la siguiente del grado.

5. Reintentar no borra lo bueno. El servidor guarda, por lección, qué ejercicios ya respondió y cuáles tuvo bien. Un acierto se queda. Si en el primer intento falló uno y en el segundo lo tiene bien, el puntaje sube. No hay forma de que un reintento baje el puntaje guardado. Ese número es el que usa la pantalla de «N sobre 100» y el círculo verde del módulo. El círculo verde solo sale si la lección está aprobada, no si apenas la terminó.

6. La cuenta. La crea el representante: su nombre, su correo, y el nombre, el grado y la escuela del estudiante. El servidor le pide a Supabase que mande un código a ese correo. Supabase genera 8 dígitos y los envía. MatiLab no inventa ese código ni lo guarda en la página: se lo manda de vuelta a Supabase para comprobarlo. Si coincide, se abre una sesión en una cookie del navegador. Esa cookie es lo que dice «esta persona ya entró». Dura horas, no queda el código a la vista. Pedir otro código seguido tiene una espera corta, para que no se pueda disparar el correo una y otra vez. Quien ya entró antes solo pone el correo y pide un código nuevo. Si Supabase no está configurado, la práctica igual corre: el código aparece en la pantalla y el progreso queda en la memoria del proceso. En matiaslab.vercel.app sí está Supabase.

7. El grado se cumple en el servidor, no solo en el dibujo del candado. La lista puede mostrar una lección de otro grado como bloqueada, pero eso no bastaría: alguien puede escribir la dirección directo. Cuando llega una respuesta, el servidor mira la sesión, mira el grado de la cuenta y mira de qué grados es esa lección. Si no coincide y no pidió el repaso, rechaza la respuesta. Aunque la pantalla fallara, la corrección no pasa. «Verla igual» deja verla y responderla. No cambia el grado guardado, y esas lecciones no entran en la cuenta de «N de M aprobadas».

8. La prueba de quien no tiene cuenta no se mezcla con el progreso. Son tres preguntas fijas: 6 + 5, 9 − 4 y 3 × 4. También se corrigen en el servidor y tampoco viaja la respuesta. No se guardan. Al terminar, el botón lleva a crear la cuenta. Si alguien que ya entró abre esa prueba, el servidor no se la muestra: lo manda a su primera lección.

9. Dónde se guarda y quién puede leerlo. Hay dos tablas: la cuenta del estudiante, con nombre, grado, correo del representante, escuela y racha, y el progreso de cada lección. El navegador no habla con esa base. Solo habla con MatiLab, y MatiLab entra con una clave que nunca se publica. Las tablas tienen la seguridad de fila activada y no hay una puerta abierta al público. Además, el navegador guarda una copia del avance para que, si se recarga la página, no se pierda lo que acaba de hacer. La copia de verdad, la que vale al volver a entrar, es la del servidor.

10. La racha. Cuenta un día de Venezuela, medianoche a medianoche, no la hora del teléfono. Hace falta haber respondido al menos un ejercicio. El mismo día no suma otra vez. Si el último día fue ayer, suma uno. Si hubo un hueco, vuelve a uno. Por eso un estudiante no alarga la racha cambiando el reloj.

11. Si algo de la base falla, la práctica no se cae. El servidor contesta igual la corrección. Marca que no pudo guardar y el avance queda en la memoria de esa visita. Cuando la base responde, vuelve a guardar ahí. Así un tropiezo de Supabase no deja al niño sin poder terminar el ejercicio.

### María Belinda

Tu parte es el frontend: lo que el niño ve y toca. Ábrelo en https://matiaslab.vercel.app y ve señalando la pantalla mientras hablas. No hace falta nombrar archivos ni colores en código.

Qué tienes que dejar claro: la pantalla está hecha para que un niño de primaria sepa, sin que nadie se lo diga, dónde mirar, qué puede pulsar y qué acaba de pasar.

1. Cómo se reconoce la página. El fondo es blanco. El texto de leer es una letra sencilla. Los títulos son una letra de libro, con más carácter, para que el nombre de la lección se distinga del enunciado. Hay un solo verde, y ese verde es siempre la acción que toca hacer ahora: Empezar, Comprobar, Seguir, Entrar. Los otros botones son discretos. El botón verde tiene una sombra debajo, como un botón de verdad: al pulsarlo, baja.

2. El inicio. Se ven cuatro tarjetas grandes, una por módulo. Aritmética es durazno, Fracciones es azul muy pálido, Geometría es verde salvia y Razonamiento es lila. Al pasar el cursor, la tarjeta se levanta un poco. Así se elige el módulo. Arriba, el menú dice Módulos siempre. Mi progreso solo aparece cuando ya hay una sesión. Al lado está Conócenos. A la derecha hay una llama: es la racha. Si ese día ya practicó, la llama se pone en el mismo durazno. El pie dice: MatiLab · Hecho con ♥ desde Venezuela.

3. Dentro de una lección, en la computadora, la pantalla se parte en dos. A la izquierda está la lección: el módulo, el título, un ejemplo y un dibujo si hace falta. «Ver la idea» está cerrado. El niño puede intentar sin leer la explicación, y abrirla si la necesita. A la derecha está la práctica. Arriba dice «Práctica 1 de 4» y una barra verde que se va llenando. Luego el enunciado. Si la respuesta es de elegir, salen cuatro pastillas. Si es de escribir, sale una casilla que dice «Tu respuesta». Abajo hay dos botones: Pista, discreto, y Comprobar, verde. Comprobar no se puede pulsar hasta que haya elegido o escrito algo.

4. Qué pasa al responder, y por qué se ve así. La opción correcta se pone verde suave y late una vez. La incorrecta se pone durazno y se sacude. Debajo aparece «Correcto» o «Incorrecto» y la explicación. La pantalla no salta sola al siguiente ejercicio: el niño tiene que leer y pulsar Seguir. Antes saltaba a los dos segundos y no daba tiempo de entender. Al terminar los cuatro, no sale un cartel enorme. Sale una tarjeta chica: «Lección completa», «Listo», el puntaje en «75 sobre 100», una frase que dice si aprobó, y recién después los botones. Si no llegó a 75, el botón verde dice «Intentar otra vez» y no «Siguiente».

5. Los dibujos no son fotos pegadas. La página los traza en el momento, del tamaño de la pantalla. Una fracción se ve como una torta partida, y cada pedazo se puede contar. También hay barras, dos tortas juntas para comparar, una suma con el signo más en el medio, y una resta donde lo que se quita queda marcado en durazno y dice «se quitan». Para repartir, se dibujan los objetos y al lado el grupo. Si la fracción es mayor que uno, no se aplasta en un solo círculo: 8/3 se ve como dos círculos enteros y un tercio. Un número mixto se ve igual: enteros completos y después el pedazo. En geometría se dibujan el triángulo, el cuadrado, el rectángulo con sus medidas, el pentágono, el corazón y la letra A para la simetría. El área del triángulo muestra la altura con una línea punteada. El ángulo recto lleva el cuadrito de la esquina. La caja se dibuja en tres caras, con largo, ancho y alto. En las opciones, si la respuesta es una fracción, al lado del texto hay una torta chiquita. El trazo de esa torta se adelgaza cuando el círculo es pequeño, porque si no, la línea tapa los cortes y el niño no puede contar.

6. El teléfono usa la misma página, no otra. El menú pasa a dos filas para que no se salga. Las cuatro tarjetas se apilan y ocupan el ancho. En la lección, primero va la idea y debajo la práctica. Los botones se estiran. Los colores y las letras no cambian. Si el teléfono pide menos movimiento, la torta no se anima y la respuesta incorrecta no se sacude.

7. Crear cuenta. El título «Crear cuenta» va centrado. Debajo, el nombre del representante y el correo. Una línea separa la sección «Estudiante», también centrada: nombre, grado y escuela. El código que llega al correo tiene 8 dígitos. La casilla deja escribir esos 8. Quien ya entró antes cambia a «Ya entré antes» y solo pone el correo.

8. Si la lección no es de su grado, no se disfraza de ejercicio. La página dice «No está en 4.º», o el grado que sea, y ofrece «Verla igual» o «Volver». En la lista del módulo, esas lecciones se marcan como repaso y no entran en la cuenta de «N de M aprobadas».

No expliques cómo el servidor corrige ni la lista de errores: eso lo cubren Gabriel y Gure. Tú enseñas la pantalla.

### Carol

Tu parte es el contenido: qué se practica, en qué grado, y con qué palabras se lo decimos a un niño. No tienes que abrir el programa. Con esta lista puedes recorrer un módulo y leer una idea, un ejemplo y una pista en voz alta.

Qué tienes que dejar claro: cada lección enseña una sola idea, con palabras de 3.º a 6.º, y la pista empuja sin regalar el resultado.

Hay 4 módulos, 32 lecciones y 128 ejercicios. Cada lección trae 4 ejercicios. En la pantalla, la idea empieza cerrada, en «Ver la idea». El ejemplo se ve de una vez. La pista solo sale si el niño pulsa Pista. La explicación completa sale después de responder, nunca antes.

Cómo está dicho, y por qué. No dejamos la palabra difícil sola. El de arriba es el numerador y el de abajo es el denominador, y así se dice en la idea: «el número de abajo dice en cuántos pedazos; el de arriba dice cuántos tomas». El residuo se presenta como «lo que sobra» y recién ahí se le pone el nombre. El vértice es «la esquina». El perímetro es «el borde, como una cerca», y se advierte que no es el espacio de adentro. El área es «lo que cabe adentro». El volumen es «cuánto cabe en la caja». La pista nunca hace la cuenta completa. Antes algunas sí la hacían, y el niño no tenía que pensar. Ahora una pista de suma dice «empieza por las de la derecha» y no escribe el resultado.

Los ejercicios mezclan la cuenta pelada y una situación: láminas, monedas de juguete, un bus, galletas, una pizza, una cerca, las edades de Camilo y su hermana. La cuenta pelada sirve para el procedimiento. La situación sirve para elegir la operación.

El orden dentro de la lección no es de arriba abajo. De los cuatro, dos son más fáciles, uno es el normal y el último es el más difícil. La práctica empieza por el normal. Si el niño falla dos veces seguidas, el siguiente es más fácil. Si acierta tres veces seguidas, cierra con el difícil. Igual recorre los cuatro. Eso se puede decir así: «no le soltamos el difícil si todavía se está enredando, y no lo dejamos solo en lo fácil si ya va seguro».

Cómo se aprueba, dicho para quien no vio la regla. Cada ejercicio vale lo mismo. Uno bien de cuatro es 25 sobre 100. Dos son 50. Tres son 75. Los cuatro son 100. La lección se aprueba con 75 o más, o sea con al menos tres bien. El módulo no se aprueba por promedio: se aprueba cuando cada lección de ese grado llega a 75. Si una se queda en 50, el módulo sigue en «2 de 4 aprobadas» y esa lección se puede intentar otra vez. El puntaje guardado no baja en el reintento.

La prueba de entrada, para quien no tiene cuenta, son tres preguntas nada más: 6 + 5, 9 − 4 y 3 × 4. No se guarda. Al terminar, el botón dice «Crear cuenta». La cuenta la abre el representante: su nombre y su correo, y después el nombre del estudiante, el grado y la escuela. El código que llega tiene 8 dígitos.

Las 32 lecciones, para que puedas nombrarlas:

Aritmética. En 3.º: sumar con llevadas y restar pidiendo prestado. En 3.º y 4.º: las tablas, dichas como grupos iguales, «4 × 3 es 4 + 4 + 4». En 4.º: multiplicar por una cifra, partiendo el número, y dividir en partes iguales. En 4.º y 5.º: la división con residuo, «caben 3 grupos y sobran 2». En 5.º: el orden de las operaciones, primero paréntesis, después multiplicar y dividir, al final sumar y restar. En 5.º y 6.º: problemas de cada día, donde primero hay que decidir si se junta, se quita, se agrupa o se reparte.

Fracciones. En 3.º: partes de un entero, con la pizza de 4 y te comes 1. En 3.º y 4.º: leerlas, medios, tercios, cuartos y octavos. En 4.º: equivalentes, 1/2 y 2/4 son la misma cantidad. En 4.º y 5.º: comparar, y sumar cuando el de abajo es el mismo. En 5.º: restar con el mismo de abajo. En 5.º y 6.º: una fracción de una cantidad, primero repartir y después tomar las partes. En 6.º: números mixtos, 7/4 es 1 entero y 3/4.

Geometría. En 3.º: las figuras planas. En 3.º y 4.º: lados y vértices. En 4.º: el perímetro. En 4.º y 5.º: el área del rectángulo. En 5.º: el área del triángulo, como la mitad de un rectángulo, y la simetría, doblar y que las dos mitades coincidan. En 5.º y 6.º: los ángulos, con la esquina de la hoja como 90 grados. En 6.º: el volumen de una caja, largo por ancho por alto.

Razonamiento. En 3.º: patrones que se repiten. En 3.º y 4.º: qué sigue, cuando la regla ya no es siempre sumar lo mismo. En 4.º: verdadero o falso. En 4.º y 5.º: deducir quién es, juntando pistas. En 5.º: clasificar. En 5.º y 6.º: caminos, contar posibilidades sin repetir. En 6.º: edades, traducir «dentro de» a suma y «hace» a resta, y pensar al revés: si el final se conoce, se deshace la cuenta.

No expliques el servidor, el diseño de los botones ni la lista de fallos: eso lo cubren Gabriel, María Belinda y Gure.

### Gure

Tu parte son los obstáculos: qué nos impidió tener el producto usable y cómo quedó resuelto. No hace falta decir cómo está programado. Cuenta cada tropiezo como una historia corta: qué veía la persona, por qué eso impedía usar MatiLab, y qué ve ahora.

1. El correo no dejaba entrar. Al crear la cuenta, Supabase mandaba un enlace mágico. Ese enlace abría la dirección del computador donde estábamos probando, no el sitio. Quien recibía el correo en el teléfono no podía entrar. Lo cambiamos para que el correo muestre el código, y Supabase manda 8 dígitos, no 6. La casilla de MatiLab acepta esos 8. La persona los copia y entra. Si en una prueba no hay correo configurado, el mismo código aparece en la pantalla, para no quedarnos trabados.

2. La respuesta correcta no puede viajar con la página. Si el ejercicio llegara con la opción buena marcada, cualquiera la vería antes de pensar. La página trae el enunciado y las opciones, nada más. El niño envía lo que eligió. El servidor responde si está bien y, recién entonces, manda la explicación. Por eso «Ver la idea» explica el procedimiento y la pista no dice el número final.

3. La práctica se iba sola. Al elegir una respuesta salía «Correcto» o «Incorrecto» y, al segundo y medio, cambiaba de ejercicio. No daba tiempo de leer por qué. Ahora la pantalla se queda ahí. La opción buena se marca, la mala se sacude, se lee la explicación y hay que pulsar Seguir. Sin ese clic no hay avance.

4. El puntaje no se entendía y no decidía nada. Al terminar decía «1 de 4». Parecía una fracción y no decía si la lección servía. Ahora dice «25 sobre 100», «50 sobre 100», «75 sobre 100» o «100 sobre 100». La regla es concreta: con 75 o más, la lección se aprueba. Tres de cuatro alcanzan. Dos de cuatro son 50 y no alcanzan. El módulo no hace promedio. Dice «2 de 4 aprobadas» hasta que cada lección del grado llega a 75, y entonces dice «Aprobado». Si no llegó, el botón verde no lleva a la lección siguiente: dice «Intentar otra vez». Repetirla no castiga: el puntaje guardado solo puede subir.

5. Terminar no era lo mismo que aprobar, y al principio lo tratábamos igual. Un estudiante podía responder los cuatro mal y la lección quedaba marcada como hecha. Ahora hay dos cosas distintas. Recorrió los cuatro, sí. Los aprobó, solo si el puntaje es 75 o más. El círculo verde del módulo sale únicamente en las aprobadas.

6. Las fracciones de las opciones no se podían contar. Dibujábamos una torta chiquita al lado de 3/8 o de 8/3, pero el trazo era tan grueso que tapaba los cortes. El niño veía una mancha, no ocho pedazos. Además, 8/3 se intentaba meter en un solo círculo. Ahora el trazo se adelgaza cuando el dibujo es pequeño, cada corte se ve, y 8/3 son dos círculos enteros más un tercio.

7. En el teléfono la página de escritorio se rompía. El menú se salía, las tarjetas no cabían y los botones quedaban apretados. No hicimos otra aplicación. La misma página, cuando la pantalla es angosta, parte el menú en dos filas, apila las tarjetas y estira los botones. En la lección, la idea queda arriba y la práctica abajo.

8. Conócenos tenía un hueco. La foto quedaba arriba y debajo sobraba un blanco grande, así que el texto y la imagen no se leían juntos. Ahora la foto va al lado del texto, centrada, con el pie de foto también centrado. En el teléfono se apilan.

9. El grado no cerraba de verdad. Un estudiante de 4.º podía escribir la dirección de una lección de 6.º y practicarla. La lista la mostraba bloqueada, pero la página no. Ahora, si no es de su grado, la página dice «No está en 4.º» y no deja responder. Si quiere verla, pulsa «Verla igual». Eso no le cambia el grado, y esas lecciones de repaso no cuentan para aprobar el módulo.

10. Las ideas y las pistas no servían para la edad. Estaban dichas como para un adulto, y varias pistas resolvían el ejercicio: decían la suma ya hecha o el resultado de la fracción. Un niño que pulsara Pista no practicaba. Las reescribimos. La idea de las fracciones habla de pedazos, la de arriba y la de abajo. La pista dice por dónde empezar y se detiene antes del resultado.

11. La tarjeta final también estorbó. Primero el título y el «75 sobre 100» salían enormes y se comían la pantalla. Los achicamos y quedaron pegados entre sí y pegados a los botones. Ahora el título es chico, el puntaje va aparte, hay aire, y los botones quedan más abajo. Se puede leer la frase de si aprobó o de que faltó el 75.

12. El registro pedía de más y se leía como un formulario de oficina. Decía «Representante» como encabezado y «El código llega a este correo». Lo dejamos en el orden en que se llena: crear cuenta, nombre y correo del representante, y después el estudiante, con su nombre, su grado y su escuela.

13. «Empezar a practicar» no tenía un primer contacto. Mandaba directo a registrarse, o a una lección, sin que el niño probara. Ahora son tres preguntas, 6 + 5, 9 − 4 y 3 × 4, y al final el botón es «Crear cuenta». Si ya hay sesión, esas tres preguntas no salen: va a su primera lección.

14. La racha no podía depender del reloj del teléfono. Si el estudiante viaja o el aparato tiene otra hora, el día se correría. La racha usa el día de Venezuela. El mismo día no suma. El día siguiente suma uno. Si se salta un día, vuelve a uno. Hace falta haber respondido al menos un ejercicio.

Con eso el producto se puede usar de punta a punta: entrar con el código de 8 dígitos, practicar sin que la pantalla se escape, ver un puntaje sobre 100 y saber si el módulo quedó aprobado. Las pruebas automáticas revisan justo estos puntos: que la explicación no salga antes de responder, que el grado bloquee, que la racha cambie de día, que la dificultad baje o suba, y que 75 sobre 100 apruebe la lección.
