"""Repertorio de MatiLab: cuatro módulos para 3.º a 6.º grado.

El contenido vive en código en esta primera versión. Así se puede revisar,
corregir y presentar sin un panel de administración.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

GRADES = (3, 4, 5, 6)

_FRACTIONS = str.maketrans(
    {"½": "1/2", "⅓": "1/3", "¼": "1/4", "¾": "3/4", "⅔": "2/3"}
)


def normalize(value: str) -> str:
    text = value.strip().lower().translate(_FRACTIONS)
    text = text.replace(" ", "").replace(",", ".")
    if re.fullmatch(r"\d+\.0+", text):
        text = text.split(".", 1)[0]
    return text


@dataclass(frozen=True)
class Problem:
    id: str
    prompt: str
    kind: str
    explain: str
    hint: str
    choices: tuple[tuple[str, str], ...] = ()
    answers: tuple[str, ...] = ()


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    summary: str
    grades: tuple[int, ...]
    idea: str
    example_prompt: str
    example_work: str
    problems: tuple[Problem, ...]

    @property
    def grade_label(self) -> str:
        return _grade_label(self.grades)


@dataclass(frozen=True)
class Module:
    slug: str
    number: int
    title: str
    blurb: str
    tint: str
    lessons: tuple[Lesson, ...]

    @property
    def grade_label(self) -> str:
        grades = sorted({grade for lesson in self.lessons for grade in lesson.grades})
        return f"{grades[0]}.º a {grades[-1]}.º"


def _grade_label(grades: tuple[int, ...]) -> str:
    ordered = tuple(sorted(grades))
    if len(ordered) == 1:
        return f"{ordered[0]}.º"
    if list(ordered) == list(range(ordered[0], ordered[-1] + 1)):
        return f"{ordered[0]}.º a {ordered[-1]}.º"
    return ", ".join(f"{grade}.º" for grade in ordered)


def _choice(prompt: str, options: list[str], answer: str, explain: str, hint: str = "") -> tuple:
    return ("choice", prompt, tuple(options), (answer,), explain, hint)


def _number(prompt: str, answers: str | tuple[str, ...], explain: str, hint: str = "") -> tuple:
    if isinstance(answers, str):
        answers = (answers,)
    return ("number", prompt, (), tuple(answers), explain, hint)


def _lesson(
    lesson_id: str,
    title: str,
    summary: str,
    grades: tuple[int, ...],
    idea: str,
    example_prompt: str,
    example_work: str,
    raw_problems: list[tuple],
) -> Lesson:
    problems: list[Problem] = []
    for index, raw in enumerate(raw_problems, start=1):
        kind, prompt, options, answers, explain, hint = raw
        problems.append(
            Problem(
                id=f"{lesson_id}-p{index}",
                prompt=prompt,
                kind=kind,
                explain=explain,
                hint=hint,
                choices=tuple((option, option) for option in options),
                answers=tuple(normalize(answer) for answer in answers),
            )
        )
    return Lesson(
        id=lesson_id,
        title=title,
        summary=summary,
        grades=grades,
        idea=idea,
        example_prompt=example_prompt,
        example_work=example_work,
        problems=tuple(problems),
    )


def _validate(modules: tuple[Module, ...]) -> None:
    seen: set[str] = set()
    for module in modules:
        if not module.lessons:
            raise ValueError(f"{module.slug} no tiene lecciones")
        for lesson in module.lessons:
            if lesson.id in seen:
                raise ValueError(f"Lección repetida: {lesson.id}")
            seen.add(lesson.id)
            if not lesson.grades or any(grade not in GRADES for grade in lesson.grades):
                raise ValueError(f"Grados inválidos en {lesson.id}")
            if len(lesson.problems) < 3:
                raise ValueError(f"{lesson.id} necesita al menos 3 prácticas")
            for problem in lesson.problems:
                if not problem.explain or not problem.prompt:
                    raise ValueError(f"{problem.id} está incompleto")
                if problem.kind == "choice":
                    labels = [label for _, label in problem.choices]
                    if len(labels) < 2 or len(set(labels)) != len(labels):
                        raise ValueError(f"{problem.id} tiene opciones inválidas")
                    if problem.answers[0] not in {normalize(label) for label in labels}:
                        raise ValueError(f"{problem.id} no incluye su respuesta entre las opciones")
                elif problem.kind != "number" or not problem.answers:
                    raise ValueError(f"{problem.id} tiene un tipo inválido")


C = _choice
N = _number

MODULES: tuple[Module, ...] = (
    Module(
        slug="aritmetica",
        number=1,
        title="Aritmética",
        blurb="Sumar, restar, multiplicar y dividir, y usar esas ideas en problemas de todos los días.",
        tint="peach",
        lessons=(
            _lesson(
                "sumar-con-llevadas",
                "Sumar con llevadas",
                "Cuando las unidades pasan de 9, llevas 1 a las decenas.",
                (3,),
                "Suma primero las unidades. Si llegan a 10 o más, escribes la unidad y llevas 1 a las decenas.",
                "18 + 5",
                "8 + 5 = 13. Escribes 3 y llevas 1. 1 + 1 = 2. El resultado es 23.",
                [
                    C("¿Cuánto es 27 + 15?", ["32", "42", "41", "52"], "42", "7 + 5 = 12. Escribes 2 y llevas 1. 2 + 1 + 1 = 4. Resultado: 42.", "Suma las unidades y no olvides lo que llevas."),
                    C("¿Cuánto es 46 + 38?", ["74", "84", "714", "85"], "84", "6 + 8 = 14. Escribes 4 y llevas 1. 4 + 3 + 1 = 8. Resultado: 84.", "6 + 8 pasa de 9."),
                    N("¿Cuánto es 109 + 26?", "135", "9 + 6 = 15. Escribes 5 y llevas 1. 0 + 2 + 1 = 3. El 1 de las centenas se queda. Resultado: 135.", "Empieza por las unidades: 9 + 6."),
                    C("Ana tiene 48 láminas y le regalan 17. ¿Cuántas tiene ahora?", ["55", "65", "61", "75"], "65", "8 + 7 = 15. Escribes 5 y llevas 1. 4 + 1 + 1 = 6. Ana tiene 65 láminas.", "Es una suma: 48 + 17."),
                ],
            ),
            _lesson(
                "restar-con-prestado",
                "Restar pidiendo prestado",
                "Si una cifra no alcanza, pides 1 a la cifra de la izquierda.",
                (3,),
                "Si la cifra de arriba es menor, tomas 1 de la siguiente columna. Esa 1 vale 10 en el lugar donde estás.",
                "32 − 15",
                "2 no alcanza para quitar 5. Pides 1 a las decenas: quedan 2 decenas y 12 unidades. 12 − 5 = 7 y 2 − 1 = 1. Resultado: 17.",
                [
                    C("¿Cuánto es 42 − 17?", ["25", "35", "29", "15"], "25", "2 no alcanza. Pides prestado: 12 − 7 = 5 y 3 − 1 = 2. Resultado: 25.", "Fíjate en las unidades primero."),
                    C("¿Cuánto es 70 − 26?", ["44", "56", "54", "46"], "44", "0 no alcanza. La decena se convierte en 10. 10 − 6 = 4 y 6 − 2 = 4. Resultado: 44.", "El 0 necesita ayuda de la cifra de al lado."),
                    N("¿Cuánto es 103 − 45?", "58", "103 − 45 = 58. Puedes comprobarlo sumando: 58 + 45 = 103.", "Puedes comprobar sumando: 58 + 45."),
                    C("Tenías 50 monedas de juguete y gastaste 18. ¿Cuántas te quedan?", ["32", "42", "28", "48"], "32", "50 − 18. El 0 pide prestado: 10 − 8 = 2 y 4 − 1 = 3. Quedan 32.", "Restar es quitar. 50 − 18."),
                ],
            ),
            _lesson(
                "tablas-de-multiplicar",
                "Las tablas de multiplicar",
                "Multiplicar es sumar el mismo número varias veces.",
                (3, 4),
                "4 × 3 significa 4 + 4 + 4, o tres grupos de 4. El orden no cambia el resultado: 4 × 3 = 3 × 4.",
                "4 × 3",
                "Tres grupos de 4 son 12. También puedes pensar 4 + 4 + 4.",
                [
                    C("¿Cuánto es 6 × 7?", ["36", "42", "48", "13"], "42", "6 × 7 = 42. Es la tabla del 6 o la del 7.", "Siete grupos de 6."),
                    C("¿Cuánto es 8 × 4?", ["24", "32", "36", "12"], "32", "8 × 4 = 32. Cuatro grupos de 8.", "8 + 8 + 8 + 8."),
                    C("¿Cuánto es 9 × 5?", ["45", "40", "14", "95"], "45", "9 × 5 = 45. Cinco grupos de 9.", "La tabla del 5 termina en 0 o en 5."),
                    C("Hay 3 cajas con 8 lápices cada una. ¿Cuántos lápices hay?", ["11", "24", "16", "32"], "24", "3 × 8 = 24 lápices.", "Son 3 grupos iguales."),
                ],
            ),
            _lesson(
                "multiplicar-dos-cifras",
                "Multiplicar por una cifra",
                "Multiplicas las unidades y después las decenas.",
                (4,),
                "Para 23 × 3, primero haces 3 × 3 = 9. Luego 2 decenas × 3 = 6 decenas. Juntas: 69.",
                "12 × 4",
                "4 × 2 = 8 unidades. 4 × 1 decena = 4 decenas. Resultado: 48.",
                [
                    C("¿Cuánto es 12 × 4?", ["16", "48", "46", "412"], "48", "4 × 2 = 8 y 4 × 10 = 40. 40 + 8 = 48.", "Multiplica 10 y 2 por separado."),
                    C("¿Cuánto es 23 × 3?", ["26", "69", "66", "29"], "69", "3 × 3 = 9 y 3 × 20 = 60. 60 + 9 = 69.", "23 es 20 + 3."),
                    N("¿Cuánto es 15 × 6?", "90", "6 × 5 = 30, llevas 3. 6 × 1 = 6, más 3 son 9. Resultado: 90.", "15 × 6 es como 10 × 6 más 5 × 6."),
                    C("Cinco paquetes traen 14 galletas cada uno. ¿Cuántas galletas hay?", ["19", "70", "64", "54"], "70", "5 × 14 = 70. 5 × 10 = 50 y 5 × 4 = 20.", "Es una multiplicación: 5 × 14."),
                ],
            ),
            _lesson(
                "dividir-en-partes",
                "Dividir en partes iguales",
                "Dividir es repartir en grupos del mismo tamaño.",
                (4,),
                "24 ÷ 6 pregunta: ¿cuántos grupos de 6 caben en 24? Como 6 × 4 = 24, el resultado es 4.",
                "18 ÷ 3",
                "3 × 6 = 18, así que 18 ÷ 3 = 6. Cada parte queda con 6.",
                [
                    C("¿Cuánto es 24 ÷ 6?", ["4", "6", "18", "3"], "4", "6 × 4 = 24, así que 24 ÷ 6 = 4.", "Busca qué número, multiplicado por 6, da 24."),
                    C("¿Cuánto es 36 ÷ 4?", ["8", "9", "6", "32"], "9", "4 × 9 = 36. El cociente es 9.", "Piensa en la tabla del 4."),
                    N("¿Cuánto es 45 ÷ 9?", "5", "9 × 5 = 45. Por eso 45 ÷ 9 = 5.", "¿Cuántas veces cabe el 9 en 45?"),
                    C("Hay 18 caramelos para 3 amigos, en partes iguales. ¿Cuántos recibe cada uno?", ["6", "15", "21", "9"], "6", "18 ÷ 3 = 6. Cada amigo recibe 6 caramelos.", "Repartir en partes iguales es dividir."),
                ],
            ),
            _lesson(
                "division-con-residuo",
                "División con residuo",
                "A veces la división no es exacta y sobra una cantidad.",
                (4, 5),
                "17 ÷ 5 cabe 3 veces, porque 5 × 3 = 15. Sobran 2. El 3 es el cociente y el 2 es el residuo.",
                "17 ÷ 5",
                "Caben 3 grupos de 5 y sobran 2. Cociente 3, residuo 2.",
                [
                    C("En 17 ÷ 5, ¿cuánto sobra?", ["1", "2", "3", "5"], "2", "5 × 3 = 15 y 17 − 15 = 2. El residuo es 2.", "Quita los grupos completos y mira lo que queda."),
                    C("¿Cuál es el cociente de 23 ÷ 4?", ["5", "3", "6", "4"], "5", "4 × 5 = 20. Cabe 5 veces y sobran 3. El cociente es 5.", "El cociente es cuántas veces cabe, no lo que sobra."),
                    N("¿Cuánto sobra al dividir 20 ÷ 6?", "2", "6 × 3 = 18 y 20 − 18 = 2. El residuo es 2.", "Busca el múltiplo de 6 que no se pase de 20."),
                    C("Tienes 31 stickers y los pegas de 7 en 7. ¿Cuántos sobran?", ["3", "4", "1", "7"], "3", "7 × 4 = 28 y 31 − 28 = 3. Sobran 3 stickers.", "4 páginas completas usan 28."),
                ],
            ),
            _lesson(
                "orden-de-operaciones",
                "Orden de las operaciones",
                "Primero paréntesis, después × y ÷, y al final + y −.",
                (5,),
                "En 3 + 4 × 2 no se suma primero. Se multiplica 4 × 2 = 8 y después 3 + 8 = 11. Los paréntesis mandan sobre todo.",
                "20 − 6 ÷ 2",
                "Primero 6 ÷ 2 = 3. Luego 20 − 3 = 17.",
                [
                    C("¿Cuánto es 3 + 4 × 2?", ["14", "11", "9", "24"], "11", "Primero 4 × 2 = 8. Después 3 + 8 = 11.", "La multiplicación va antes que la suma."),
                    C("¿Cuánto es (3 + 4) × 2?", ["14", "11", "10", "9"], "14", "El paréntesis se resuelve primero: 3 + 4 = 7. Luego 7 × 2 = 14.", "Los paréntesis se hacen antes."),
                    N("¿Cuánto es 20 − 6 ÷ 2?", "17", "6 ÷ 2 = 3 y 20 − 3 = 17.", "Divide antes de restar."),
                    N("¿Cuánto es 2 × (8 − 3) + 1?", "11", "8 − 3 = 5. Luego 2 × 5 = 10. Al final 10 + 1 = 11.", "Empieza por el paréntesis."),
                ],
            ),
            _lesson(
                "problemas-de-cada-dia",
                "Problemas de cada día",
                "Lees el problema, eliges la operación y compruebas si el resultado tiene sentido.",
                (5, 6),
                "Un problema cuenta una situación. Pregúntate: ¿junto grupos iguales, reparto, agrego o quito? Después haz la cuenta y revisa.",
                "Un bus lleva 36 niños y cada fila tiene 4 asientos. ¿Cuántas filas se ocupan?",
                "Se reparten 36 en grupos de 4. 36 ÷ 4 = 9 filas.",
                [
                    C("Un bus lleva 36 niños. Cada fila tiene 4 asientos. ¿Cuántas filas se ocupan?", ["9", "32", "40", "8"], "9", "36 ÷ 4 = 9 filas.", "Repartir en filas iguales es dividir."),
                    N("Compras 3 paquetes de 12 crayones y regalas 5. ¿Cuántos te quedan?", "31", "3 × 12 = 36 y 36 − 5 = 31.", "Primero junta los paquetes y después quita los que regalas."),
                    N("Cada entrada cuesta 8. Compras 4 y pagas con 50. ¿Cuánto te devuelven?", "18", "4 × 8 = 32. 50 − 32 = 18.", "Calcula el costo y réstalo de 50."),
                    N("Durante 5 días haces 6 ejercicios por día. Ya hiciste 11. ¿Cuántos te faltan?", "19", "5 × 6 = 30 ejercicios en total. 30 − 11 = 19.", "Halla el total y quita los que ya hiciste."),
                ],
            ),
        ),
    ),
    Module(
        slug="fracciones",
        number=2,
        title="Fracciones",
        blurb="Partir un entero en partes iguales, compararlas y hallar una fracción de una cantidad.",
        tint="blue",
        lessons=(
            _lesson(
                "partes-de-un-entero",
                "Partes de un entero",
                "El denominador dice en cuántas partes iguales se corta. El numerador dice cuántas tomas.",
                (3,),
                "En 3/8, el 8 es el denominador: el entero se partió en 8 partes iguales. El 3 es el numerador: tomamos 3 de esas partes.",
                "Una pizza se corta en 4 partes iguales y comes 1.",
                "Comes 1 de 4 partes iguales. La fracción es 1/4.",
                [
                    C("Una pizza se corta en 4 partes iguales y comes 1. ¿Qué fracción comiste?", ["1/2", "1/4", "4/1", "3/4"], "1/4", "Tomaste 1 parte de 4 iguales: 1/4.", "El número de abajo cuenta las partes iguales."),
                    C("Un chocolate se parte en 8 y tomas 3. ¿Qué fracción tomas?", ["3/8", "8/3", "3/5", "5/8"], "3/8", "3 partes de 8 iguales: 3/8.", "Numerador 3, denominador 8."),
                    C("¿Qué número dice en cuántas partes iguales se divide el entero?", ["El numerador", "El denominador", "El residuo", "El cociente"], "El denominador", "El denominador, el número de abajo, cuenta las partes iguales.", "Está escrito debajo de la raya."),
                    C("Pintas 2 de 6 partes iguales. ¿Qué fracción pintaste?", ["6/2", "2/6", "2/4", "4/6"], "2/6", "Pintaste 2 partes de 6: 2/6.", "Cuentas las pintadas arriba y el total abajo."),
                ],
            ),
            _lesson(
                "leer-fracciones",
                "Leer y escribir fracciones",
                "Cada denominador tiene un nombre: medios, tercios, cuartos, octavos.",
                (3, 4),
                "1/2 se lee un medio. 2/3 se lee dos tercios. 3/4 se lee tres cuartos. El nombre sale del denominador.",
                "3/4",
                "Se lee tres cuartos: tres partes de cuatro iguales.",
                [
                    C("¿Cómo se lee 2/3?", ["Dos medios", "Dos tercios", "Tres medios", "Tres cuartos"], "Dos tercios", "El denominador 3 se llama tercios. 2/3 es dos tercios.", "El 3 da el nombre."),
                    C("¿Cómo se lee 1/2?", ["Un cuarto", "Un medio", "Dos medios", "Un tercio"], "Un medio", "1/2 es un medio: una de dos partes iguales.", "Partir en dos es hacer mitades."),
                    C("¿Cómo se lee 3/4?", ["Tres medios", "Cuatro tercios", "Tres cuartos", "Tres octavos"], "Tres cuartos", "El 4 se llama cuartos. 3/4 es tres cuartos.", "Piensa en una pizza de 4 porciones."),
                    C("¿Cómo se lee 5/8?", ["Cinco octavos", "Ocho quintos", "Cinco cuartos", "Cinco medios"], "Cinco octavos", "El denominador 8 se llama octavos. 5/8 es cinco octavos.", "Ocho partes iguales, tomas cinco."),
                ],
            ),
            _lesson(
                "fracciones-equivalentes",
                "Fracciones equivalentes",
                "Dos fracciones son equivalentes cuando nombran la misma cantidad.",
                (4,),
                "1/2 y 2/4 ocupan la misma parte del entero. Si multiplicas o divides el numerador y el denominador por el mismo número, la fracción vale lo mismo.",
                "1/2 y 2/4",
                "2 ÷ 2 = 1 y 4 ÷ 2 = 2. Por eso 2/4 = 1/2. Son equivalentes.",
                [
                    C("¿Cuál es equivalente a 1/2?", ["2/4", "2/3", "1/3", "3/4"], "2/4", "1 × 2 = 2 y 2 × 2 = 4. 1/2 = 2/4.", "Multiplica arriba y abajo por 2."),
                    C("¿Cuál es equivalente a 1/3?", ["2/6", "2/3", "3/6", "1/6"], "2/6", "1 × 2 = 2 y 3 × 2 = 6. 1/3 = 2/6.", "El mismo factor arriba y abajo."),
                    C("¿2/4 y 1/2 son equivalentes?", ["Sí", "No"], "Sí", "2/4 simplificada, dividiendo entre 2, es 1/2. Nombran la misma cantidad.", "Dibuja un entero a la mitad y otro en cuatro partes con dos pintadas."),
                    C("¿Cuál es equivalente a 3/6?", ["1/2", "2/3", "1/3", "3/3"], "1/2", "3 ÷ 3 = 1 y 6 ÷ 3 = 2. 3/6 = 1/2.", "Divide arriba y abajo entre 3."),
                ],
            ),
            _lesson(
                "comparar-fracciones",
                "Comparar fracciones",
                "Con el mismo entero, puedes decir cuál fracción es mayor.",
                (4, 5),
                "Si el denominador es igual, gana el numerador mayor: 5/8 > 3/8. Si el numerador es 1, gana el denominador menor: 1/2 > 1/4, porque las partes son más grandes.",
                "¿Qué es mayor, 1/2 o 1/4?",
                "Un medio es más grande que un cuarto. 1/2 se lleva la mitad del entero y 1/4 solo una de cuatro partes.",
                [
                    C("¿Qué es mayor?", ["1/2", "1/4", "Son iguales"], "1/2", "La mitad es más grande que un cuarto del mismo entero.", "Entre más partes iguales, cada parte es más pequeña."),
                    C("¿Qué es mayor, 2/3 o 1/3?", ["2/3", "1/3", "Son iguales"], "2/3", "El denominador es el mismo. 2 partes son más que 1 parte.", "Mismo tamaño de parte: compara cuántas tomas."),
                    C("¿Qué pasa con 1/2 y 2/4?", ["1/2 es mayor", "2/4 es mayor", "Son iguales"], "Son iguales", "2/4 es equivalente a 1/2. No hay una mayor.", "Simplifica 2/4."),
                    C("¿Qué es mayor, 3/8 o 5/8?", ["3/8", "5/8", "Son iguales"], "5/8", "Las partes son octavos. Cinco octavos son más que tres octavos.", "Mira solo los numeradores."),
                ],
            ),
            _lesson(
                "sumar-fracciones",
                "Sumar fracciones",
                "Si el denominador es el mismo, sumas los numeradores y lo dejas igual.",
                (4, 5),
                "1/5 + 2/5 = 3/5. No se suman los denominadores: las partes siguen siendo quintos.",
                "1/5 + 2/5",
                "1 + 2 = 3 numeradores. El denominador sigue siendo 5. Resultado: 3/5.",
                [
                    C("¿Cuánto es 1/5 + 2/5?", ["3/5", "3/10", "2/5", "1/5"], "3/5", "1 + 2 = 3 y el denominador no cambia: 3/5.", "Suma solo los de arriba."),
                    C("¿Cuánto es 2/8 + 3/8?", ["5/8", "5/16", "6/8", "1/8"], "5/8", "2 + 3 = 5. Los octavos se quedan: 5/8.", "Mismo denominador, se conserva."),
                    N("¿Cuánto es 1/4 + 1/4? Puedes simplificar.", ("2/4", "1/2"), "1 + 1 = 2, así que es 2/4. Y 2/4 equivale a 1/2.", "Suma los numeradores. Después, si quieres, divide entre 2."),
                    N("¿Cuánto es 3/10 + 4/10?", "7/10", "3 + 4 = 7. El resultado es 7/10.", "Los décimos no se suman entre sí."),
                ],
            ),
            _lesson(
                "restar-fracciones",
                "Restar fracciones",
                "Con el mismo denominador, restas los numeradores.",
                (5,),
                "4/6 − 1/6 = 3/6. Quitas partes del mismo tamaño. El denominador se queda.",
                "5/7 − 2/7",
                "5 − 2 = 3. Quedan 3/7.",
                [
                    N("¿Cuánto es 4/6 − 1/6? Puedes simplificar.", ("3/6", "1/2"), "4 − 1 = 3, así que es 3/6. Eso equivale a 1/2.", "Resta los numeradores."),
                    N("¿Cuánto es 5/7 − 2/7?", "3/7", "5 − 2 = 3. El resultado es 3/7.", "Los séptimos se mantienen."),
                    N("¿Cuánto es 3/4 − 1/4? Puedes simplificar.", ("2/4", "1/2"), "3 − 1 = 2. Queda 2/4, que es 1/2.", "Quita un cuarto de tres cuartos."),
                    C("Tenías 7/8 de un litro y usaste 2/8. ¿Cuánto queda?", ["5/8", "9/8", "5/16", "2/8"], "5/8", "7 − 2 = 5. Quedan 5/8 de litro.", "Misma unidad: octavos de litro."),
                ],
            ),
            _lesson(
                "fraccion-de-una-cantidad",
                "Fracción de una cantidad",
                "Para hallar una fracción de un número, divides y después multiplicas si hace falta.",
                (5, 6),
                "1/4 de 20: divides 20 entre 4 y obtienes 5. 2/3 de 9: divides 9 entre 3, que da 3, y multiplicas por 2. Resultado: 6.",
                "1/2 de 10",
                "La mitad de 10 es 10 ÷ 2 = 5.",
                [
                    C("¿Cuánto es 1/2 de 10?", ["2", "5", "8", "20"], "5", "10 ÷ 2 = 5. Un medio de 10 es 5.", "Mitad significa dividir entre 2."),
                    C("¿Cuánto es 1/4 de 20?", ["4", "5", "10", "16"], "5", "20 ÷ 4 = 5. Un cuarto de 20 es 5.", "Parte 20 en 4 grupos iguales."),
                    N("¿Cuánto es 2/3 de 9?", "6", "9 ÷ 3 = 3 y 3 × 2 = 6.", "Primero halla un tercio y luego toma dos."),
                    N("¿Cuánto es 3/5 de 15?", "9", "15 ÷ 5 = 3 y 3 × 3 = 9.", "Un quinto de 15 es 3. Tres quintos son 9."),
                ],
            ),
            _lesson(
                "numeros-mixtos",
                "Números mixtos",
                "Un número mixto junta enteros y una fracción. Una fracción mayor que 1 se puede escribir así.",
                (6,),
                "7/4 es más que un entero, porque 4/4 = 1. Sobran 3/4. Entonces 7/4 = 1 entero y 3/4.",
                "7/4",
                "4/4 forman 1 entero y sobran 3/4. Se escribe 1 3/4.",
                [
                    N("En 7/4, ¿cuántos enteros completos hay?", "1", "4/4 es un entero y sobran 3 cuartos. Hay 1 entero.", "¿Cuántas veces cabe el denominador en el numerador?"),
                    N("¿Qué fracción impropia es 1 entero y 1/2?", "3/2", "1 entero es 2/2. Más 1/2 da 3/2.", "Convierte el entero en medios y suma."),
                    N("De 11/3, después de sacar los enteros, ¿cuántos tercios sobran?", "2", "3 × 3 = 9, así que hay 3 enteros. 11 − 9 = 2. Sobran 2/3.", "Mira el residuo de 11 ÷ 3."),
                    N("Escribe 2 enteros y 1/4 como fracción impropia.", "9/4", "2 enteros son 8/4. Más 1/4 da 9/4.", "Cada entero aporta 4 cuartos."),
                ],
            ),
        ),
    ),
    Module(
        slug="geometria",
        number=3,
        title="Geometría",
        blurb="Figuras, perímetro, área, ángulos y el espacio que ocupa una caja.",
        tint="green",
        lessons=(
            _lesson(
                "figuras-planas",
                "Figuras planas",
                "Cada figura se reconoce por sus lados y por su forma.",
                (3,),
                "El triángulo tiene 3 lados. El cuadrado tiene 4 lados iguales. El rectángulo tiene 4 lados y los opuestos iguales. El círculo es redondo y no tiene lados rectos.",
                "Una figura de 3 lados rectos",
                "Es un triángulo.",
                [
                    C("¿Cómo se llama la figura de 3 lados?", ["Cuadrado", "Triángulo", "Círculo", "Rectángulo"], "Triángulo", "Tres lados rectos forman un triángulo.", "Cuenta los lados."),
                    C("¿Qué figura tiene 4 lados iguales y 4 esquinas iguales?", ["Rectángulo", "Triángulo", "Cuadrado", "Círculo"], "Cuadrado", "El cuadrado tiene los cuatro lados de la misma longitud.", "No basta con tener 4 lados: también son iguales."),
                    C("¿Qué figura no tiene lados rectos?", ["Triángulo", "Cuadrado", "Rectángulo", "Círculo"], "Círculo", "El círculo es una curva cerrada. No tiene lados ni vértices.", "Piensa en una moneda."),
                    C("Tiene 4 lados y los opuestos son iguales, pero no todos miden lo mismo. ¿Qué es?", ["Cuadrado", "Rectángulo", "Triángulo", "Círculo"], "Rectángulo", "En el rectángulo, los lados de enfrente coinciden y no todos son iguales, como en el cuadrado.", "Una puerta suele tener esta forma."),
                ],
            ),
            _lesson(
                "lados-y-vertices",
                "Lados y vértices",
                "Un vértice es la esquina donde se juntan dos lados.",
                (3, 4),
                "Puedes contar lados y vértices por separado. En un triángulo hay 3 lados y 3 vértices. En un cuadrado y en un rectángulo hay 4 y 4.",
                "Un triángulo",
                "Tiene 3 lados y 3 vértices.",
                [
                    C("¿Cuántos vértices tiene un triángulo?", ["2", "3", "4", "6"], "3", "Cada esquina es un vértice. El triángulo tiene 3.", "Cuenta las puntas."),
                    C("¿Cuántos lados tiene un cuadrado?", ["3", "4", "5", "8"], "4", "El cuadrado tiene 4 lados.", "Recorre el contorno."),
                    N("¿Cuántos lados tiene un pentágono?", "5", "Un pentágono tiene 5 lados.", "Penta significa cinco."),
                    C("¿Cuántos vértices tiene un rectángulo?", ["3", "4", "6", "8"], "4", "El rectángulo tiene 4 esquinas, así que tiene 4 vértices.", "Las esquinas son los vértices."),
                ],
            ),
            _lesson(
                "perimetro",
                "Perímetro",
                "El perímetro es la suma de todos los lados: el borde de la figura.",
                (4,),
                "No se cuenta el interior. Se suman las longitudes del contorno. Un cuadrado de lado 5 tiene perímetro 5 + 5 + 5 + 5 = 20.",
                "Cuadrado de lado 5",
                "4 × 5 = 20. El perímetro mide 20.",
                [
                    C("Un cuadrado tiene lado 5. ¿Cuál es su perímetro?", ["10", "20", "25", "15"], "20", "Hay 4 lados de 5. 4 × 5 = 20.", "Suma el borde, no el interior."),
                    C("Un rectángulo mide 6 de largo y 3 de ancho. ¿Cuál es su perímetro?", ["18", "9", "24", "12"], "18", "6 + 3 + 6 + 3 = 18. También 2 × (6 + 3) = 18.", "Hay dos largos y dos anchos."),
                    N("Un triángulo tiene lados 4, 4 y 3. ¿Cuál es su perímetro?", "11", "4 + 4 + 3 = 11.", "Suma los tres lados."),
                    N("Un patio rectangular mide 8 m por 2 m. ¿Cuántos metros de cerca lo rodean?", "20", "El perímetro es 8 + 2 + 8 + 2 = 20 metros.", "La cerca va por el borde."),
                ],
            ),
            _lesson(
                "area-del-rectangulo",
                "Área del rectángulo",
                "El área dice cuánta superficie cubre la figura.",
                (4, 5),
                "En un rectángulo, el área es largo × ancho. Un cuadrado es un rectángulo especial: lado × lado.",
                "Rectángulo de 4 por 3",
                "4 × 3 = 12. El área es 12 unidades cuadradas.",
                [
                    C("Un rectángulo mide 4 por 3. ¿Cuál es su área?", ["7", "12", "14", "24"], "12", "4 × 3 = 12 unidades cuadradas.", "Área es largo por ancho."),
                    C("¿Cuál es el área de un rectángulo de 7 por 2?", ["9", "14", "18", "28"], "14", "7 × 2 = 14.", "Multiplica los dos lados distintos."),
                    N("Un cuadrado tiene lado 6. ¿Cuál es su área?", "36", "6 × 6 = 36.", "En el cuadrado, largo y ancho son el mismo lado."),
                    N("Una huerta mide 5 m por 4 m. ¿Cuál es su área?", "20", "5 × 4 = 20 metros cuadrados.", "La unidad de área es el metro cuadrado."),
                ],
            ),
            _lesson(
                "area-del-triangulo",
                "Área del triángulo",
                "El área de un triángulo es base × altura ÷ 2.",
                (5,),
                "Un triángulo es la mitad de un rectángulo con la misma base y la misma altura. Por eso divides entre 2 después de multiplicar.",
                "Base 6 y altura 4",
                "6 × 4 = 24. 24 ÷ 2 = 12. El área es 12.",
                [
                    N("Base 6 y altura 4. ¿Cuál es el área?", "12", "6 × 4 = 24 y 24 ÷ 2 = 12.", "Multiplica y luego parte a la mitad."),
                    N("Base 10 y altura 3. ¿Cuál es el área?", "15", "10 × 3 = 30 y 30 ÷ 2 = 15.", "No olvides dividir entre 2."),
                    N("Base 8 y altura 5. ¿Cuál es el área?", "20", "8 × 5 = 40 y 40 ÷ 2 = 20.", "La altura baja en ángulo recto hasta la base."),
                    N("Base 7 y altura 2. ¿Cuál es el área?", "7", "7 × 2 = 14 y 14 ÷ 2 = 7.", "Catorce partidos por la mitad son 7."),
                ],
            ),
            _lesson(
                "simetria",
                "Simetría",
                "Un eje de simetría parte la figura en dos mitades que coinciden al doblarla.",
                (5,),
                "Si doblas por el eje, una mitad cae exactamente sobre la otra. Un cuadrado tiene varios ejes. Un círculo tiene infinitos.",
                "La letra A mayúscula",
                "Tiene un eje vertical: la mitad izquierda y la derecha coinciden.",
                [
                    C("¿El cuadrado tiene eje de simetría?", ["Sí", "No"], "Sí", "Puedes doblarlo por la mitad vertical, horizontal o por las diagonales.", "Piensa en doblar un papel cuadrado."),
                    C("¿La letra A mayúscula tiene un eje vertical?", ["Sí", "No"], "Sí", "La A queda igual a los dos lados de una línea vertical por el centro.", "Imagina un espejo en el medio."),
                    C("¿Cuántos ejes de simetría tiene un círculo?", ["0", "1", "4", "Infinitos"], "Infinitos", "Cualquier diámetro parte el círculo en dos mitades iguales. Hay infinitos diámetros.", "Puedes trazar un diámetro en cualquier dirección."),
                    C("Un corazón típico, ¿cuántos ejes de simetría tiene?", ["0", "1", "2", "4"], "1", "Solo el eje vertical deja las dos mitades iguales.", "La parte de arriba no coincide con la de abajo."),
                ],
            ),
            _lesson(
                "angulos",
                "Ángulos",
                "Un ángulo mide la abertura entre dos lados que se juntan.",
                (5, 6),
                "El ángulo recto mide 90 grados: es la esquina de una hoja. Si mide menos, es agudo. Si mide más de 90 y menos de 180, es obtuso.",
                "La esquina de una hoja de papel",
                "Es un ángulo recto. Mide 90 grados.",
                [
                    C("¿Cuánto mide un ángulo recto?", ["45 grados", "90 grados", "180 grados", "60 grados"], "90 grados", "El ángulo recto mide 90 grados.", "Es la esquina de una hoja."),
                    C("Un ángulo menor que 90 grados es…", ["Recto", "Agudo", "Obtuso", "Llano"], "Agudo", "Si la abertura es más cerrada que la esquina de la hoja, el ángulo es agudo.", "Agudo es más pequeño que el recto."),
                    C("Un ángulo mayor que 90 y menor que 180 grados es…", ["Agudo", "Recto", "Obtuso", "Completo"], "Obtuso", "Está más abierto que un recto, pero no llega a ser una línea recta.", "Obtuso significa más abierto que 90."),
                    C("¿Qué ángulo es la esquina de una hoja de papel?", ["Agudo", "Recto", "Obtuso", "Llano"], "Recto", "Las esquinas de la hoja son ángulos rectos.", "Miden 90 grados."),
                ],
            ),
            _lesson(
                "volumen-de-una-caja",
                "Volumen de una caja",
                "El volumen dice cuánto espacio ocupa un cuerpo, o cuánto cabe dentro.",
                (6,),
                "En una caja rectangular, el volumen es largo × ancho × alto. Un cubo tiene las tres medidas iguales.",
                "Caja de 2 × 3 × 4",
                "2 × 3 = 6 y 6 × 4 = 24. El volumen es 24 unidades cúbicas.",
                [
                    N("Una caja mide 2 × 3 × 4. ¿Cuál es su volumen?", "24", "2 × 3 × 4 = 24.", "Multiplica las tres medidas."),
                    N("Un cubo tiene lado 3. ¿Cuál es su volumen?", "27", "3 × 3 × 3 = 27.", "En el cubo, largo, ancho y alto son iguales."),
                    N("Una caja mide 5 × 2 × 2. ¿Cuál es su volumen?", "20", "5 × 2 × 2 = 20.", "Puedes hacer 10 × 2."),
                    N("Una caja mide 10 × 4 × 3. ¿Cuál es su volumen?", "120", "10 × 4 = 40 y 40 × 3 = 120.", "Multiplica de dos en dos."),
                ],
            ),
        ),
    ),
    Module(
        slug="razonamiento",
        number=4,
        title="Razonamiento lógico",
        blurb="Patrones, pistas y problemas para pensar con calma antes de calcular.",
        tint="lilac",
        lessons=(
            _lesson(
                "patrones",
                "Patrones que se repiten",
                "Un patrón es una regla que se repite. Cuando la descubres, sabes qué sigue.",
                (3,),
                "En 2, 4, 6, 8 la regla es sumar 2. En rojo, azul, rojo, azul la regla es alternar los colores.",
                "2, 4, 6, 8, …",
                "Se suma 2 cada vez. Sigue el 10.",
                [
                    C("¿Qué sigue? 2, 4, 6, 8, …", ["9", "10", "12", "16"], "10", "La regla es +2. Después de 8 viene 10.", "Mira cuánto crece de un número al siguiente."),
                    C("¿Qué sigue? Rojo, azul, rojo, azul, …", ["Rojo", "Azul", "Verde", "Amarillo"], "Rojo", "Los colores se turnan. Después de azul vuelve el rojo.", "La serie tiene dos elementos que se alternan."),
                    C("¿Qué sigue? 5, 10, 15, 20, …", ["21", "25", "30", "22"], "25", "Cuenta de 5 en 5. Después de 20 viene 25.", "Es la tabla del 5."),
                    C("¿Qué sigue? Triángulo, círculo, triángulo, círculo, …", ["Círculo", "Triángulo", "Cuadrado", "Rectángulo"], "Triángulo", "Se alternan triángulo y círculo. Toca de nuevo el triángulo.", "El patrón usa dos figuras."),
                ],
            ),
            _lesson(
                "que-sigue",
                "Qué sigue en la serie",
                "La regla puede sumar, restar o ir cambiando de a poco.",
                (3, 4),
                "No siempre se suma lo mismo. En 2, 3, 5, 8, 12 las diferencias son 1, 2, 3 y 4. La siguiente diferencia es 5.",
                "1, 2, 4, 8, …",
                "Cada número es el doble del anterior. Sigue el 16.",
                [
                    C("¿Qué sigue? 1, 2, 4, 8, …", ["10", "12", "16", "9"], "16", "Cada término se duplica. 8 × 2 = 16.", "Compara cada número con el anterior."),
                    C("¿Qué sigue? 20, 17, 14, 11, …", ["8", "9", "10", "7"], "8", "Se resta 3 cada vez. 11 − 3 = 8.", "La serie baja."),
                    N("¿Qué sigue? 3, 6, 9, 12, …", "15", "Suma 3 cada vez. 12 + 3 = 15.", "Es contar de 3 en 3."),
                    N("¿Qué sigue? 2, 3, 5, 8, 12, …", "17", "Las diferencias son 1, 2, 3 y 4. La siguiente es 5. 12 + 5 = 17.", "Mira cómo cambia el salto."),
                ],
            ),
            _lesson(
                "verdadero-o-falso",
                "Verdadero o falso",
                "Lees una frase con calma y decides si siempre es cierta.",
                (4,),
                "Una frase es verdadera si coincide con la matemática. Es falsa si encuentras un caso que no cumple, o si la cuenta está mal.",
                "Si sumas 0 a un número, el número queda igual.",
                "Es verdadero. 7 + 0 = 7 y lo mismo pasa con cualquier número.",
                [
                    C("Si sumas 0 a un número, el número queda igual.", ["Verdadero", "Falso"], "Verdadero", "Sumar 0 no cambia la cantidad.", "Prueba con 7 + 0."),
                    C("La mitad de 10 es 6.", ["Verdadero", "Falso"], "Falso", "La mitad de 10 es 5, no 6.", "10 ÷ 2 = 5."),
                    C("Un triángulo tiene 4 vértices.", ["Verdadero", "Falso"], "Falso", "Un triángulo tiene 3 vértices.", "Cuenta las esquinas."),
                    C("2 × 5 es igual a 5 × 2.", ["Verdadero", "Falso"], "Verdadero", "Las dos cuentas dan 10. En la multiplicación, el orden no cambia el producto.", "Haz las dos multiplicaciones."),
                ],
            ),
            _lesson(
                "quien-es",
                "Deduce quién es",
                "Las pistas se leen juntas. Cada una quita una posibilidad.",
                (4, 5),
                "Anota lo que sabes y lo que queda prohibido. Cuando solo queda una opción, esa es la respuesta.",
                "María es más alta que Pedro. Pedro es más alto que Lucía.",
                "Lucía es más baja que Pedro y Pedro es más bajo que María. La más baja es Lucía.",
                [
                    C("María es más alta que Pedro. Pedro es más alto que Lucía. ¿Quién es la persona más baja?", ["María", "Pedro", "Lucía"], "Lucía", "Lucía es más baja que Pedro, y Pedro es más bajo que María.", "Ordénalos de mayor a menor."),
                    C("Ana llega antes que Luis. Luis llega antes que Sofía. ¿Quién llega primero?", ["Ana", "Luis", "Sofía"], "Ana", "Ana está delante de Luis y Luis delante de Sofía. Ana llega primero.", "El que está antes que los otros dos."),
                    C("El pájaro va delante del gato y el gato va delante del perro. ¿Quién va primero?", ["El perro", "El gato", "El pájaro"], "El pájaro", "El pájaro está delante del gato, así que también está delante del perro.", "Sigue la cadena hacia el frente."),
                    C("Los números son 2, 5 y 9. El mayor no es 5 y el menor no es 9. ¿Cuál está en el medio?", ["2", "5", "9"], "5", "El mayor es 9 y el menor es 2. En el medio queda 5.", "Ordena 2, 5 y 9."),
                ],
            ),
            _lesson(
                "clasificar",
                "Clasificar",
                "Agrupar es poner juntos los elementos que comparten una regla.",
                (5,),
                "Elige una regla clara: fruta o verdura, par o impar, múltiplo o no. Después cuenta solo el grupo que pide la pregunta.",
                "2, 3, 4, 6 y 9. ¿Cuántos son pares?",
                "Los pares son 2, 4 y 6. Hay 3.",
                [
                    C("Manzana, zanahoria, banana y brócoli. ¿Cuáles son frutas?", ["Manzana y banana", "Zanahoria y brócoli", "Manzana y zanahoria", "Las cuatro"], "Manzana y banana", "La manzana y la banana son frutas. La zanahoria y el brócoli son verduras.", "Separa por el tipo de alimento."),
                    N("En 2, 3, 4, 6 y 9, ¿cuántos números son pares?", "3", "2, 4 y 6 son pares. El 3 y el 9 no. Hay 3.", "Un par termina en 0, 2, 4, 6 u 8."),
                    C("¿Cuál no pertenece a 3, 6, 9, 10?", ["3", "6", "9", "10"], "10", "3, 6 y 9 son múltiplos de 3. 10 no lo es.", "Busca la regla de los otros tres."),
                    C("Triángulo, cuadrado, círculo y rectángulo. ¿Cuál no tiene lados rectos?", ["Triángulo", "Cuadrado", "Círculo", "Rectángulo"], "Círculo", "El círculo no tiene lados rectos. Las otras tres figuras sí.", "Recuerda las figuras planas."),
                ],
            ),
            _lesson(
                "caminos",
                "Caminos y decisiones",
                "Cuentas las posibilidades sin saltarte ninguna y sin repetir.",
                (5, 6),
                "Si puedes moverte solo a la derecha o hacia arriba, escribe las rutas. Con 2 pasos a la derecha y 1 hacia arriba hay 3 órdenes distintos.",
                "Dos cuadras a la derecha y una hacia arriba.",
                "Los caminos son derecha-derecha-arriba, derecha-arriba-derecha y arriba-derecha-derecha. Hay 3.",
                [
                    C("Para ir de casa al parque das 2 cuadras a la derecha y 1 hacia arriba, en cualquier orden. ¿Cuántos caminos distintos hay?", ["2", "3", "4", "6"], "3", "Los tres órdenes son DDU, DUD y UDD.", "El paso hacia arriba puede ir primero, en medio o al final."),
                    C("Una lámpara está encendida. Pulsas el interruptor 5 veces. ¿Cómo queda?", ["Encendida", "Apagada"], "Apagada", "Cada pulso cambia el estado. Un número impar de pulsos la deja al revés de como empezó.", "Prueba con 1 pulso y luego con 3."),
                    N("Empiezas en 0 y cada paso suma 2. Después de 4 pasos, ¿en qué número estás?", "8", "2 + 2 + 2 + 2 = 8. También 4 × 2 = 8.", "Cuatro saltos de 2."),
                    C("Tienes las llaves A y B, y el orden importa. ¿Cuántos órdenes distintos hay?", ["1", "2", "4", "8"], "2", "Puedes usar primero A y luego B, o primero B y luego A. Hay 2 órdenes.", "Lista las dos secuencias."),
                ],
            ),
            _lesson(
                "edades",
                "Edades y cantidades",
                "Traduces las palabras ahora, antes y después a sumas o restas.",
                (6,),
                "Ahora es el dato de partida. Dentro de 4 años se suma 4. Hace 2 años se resta 2. Si alguien tiene 3 años menos, restas 3.",
                "Camilo tiene 10 años. Su hermana tiene 3 años menos.",
                "10 − 3 = 7. La hermana tiene 7 años.",
                [
                    N("Camilo tiene 10 años. Su hermana tiene 3 menos. ¿Cuántos años tiene ella?", "7", "10 − 3 = 7.", "Menos significa restar."),
                    N("Camilo tiene 10. ¿Cuántos años tendrá dentro de 4 años?", "14", "10 + 4 = 14.", "Dentro de unos años se suma."),
                    N("Camilo tiene 10 y su hermana 7. ¿Cuánto suman sus edades hoy?", "17", "10 + 7 = 17.", "Sumar las dos edades de ahora."),
                    N("La hermana tiene 7. ¿Cuántos años tenía hace 2 años?", "5", "7 − 2 = 5.", "Hace unos años se resta."),
                ],
            ),
            _lesson(
                "pensar-al-reves",
                "Pensar al revés",
                "Si conoces el final de la cuenta, deshaces las operaciones para hallar el inicio.",
                (6,),
                "Sumar se deshace restando. Multiplicar se deshace dividiendo. Deshaz desde la última operación hacia la primera.",
                "Pienso un número, le sumo 5 y obtengo 12.",
                "Al revés: 12 − 5 = 7. El número es 7.",
                [
                    N("Pienso un número, le sumo 5 y obtengo 12. ¿Cuál es?", "7", "12 − 5 = 7.", "Quita lo que se sumó."),
                    N("Lo multiplico por 3 y obtengo 18. ¿Cuál es el número?", "6", "18 ÷ 3 = 6.", "Dividir deshace la multiplicación."),
                    N("Lo divido entre 2 y obtengo 9. ¿Cuál es el número?", "18", "9 × 2 = 18.", "Multiplicar deshace la división."),
                    N("Le resto 4 y después multiplico por 2. Obtengo 10. ¿Cuál es el número?", "9", "Primero deshaz el ×2: 10 ÷ 2 = 5. Ese 5 es el número menos 4. 5 + 4 = 9.", "Empieza por la última operación."),
                ],
            ),
        ),
    ),
)

_validate(MODULES)

LESSONS: dict[str, tuple[Module, Lesson]] = {
    lesson.id: (module, lesson) for module in MODULES for lesson in module.lessons
}


def lesson_by_id(lesson_id: str) -> Lesson | None:
    found = LESSONS.get(lesson_id)
    return found[1] if found else None


def module_by_slug(slug: str) -> Module | None:
    for module in MODULES:
        if module.slug == slug:
            return module
    return None


def module_of(lesson_id: str) -> Module | None:
    found = LESSONS.get(lesson_id)
    return found[0] if found else None


def visible_lessons(module: Module, grade: int | None) -> tuple[Lesson, ...]:
    if grade is None:
        return module.lessons
    return tuple(lesson for lesson in module.lessons if grade in lesson.grades)


def next_lesson(lesson_id: str, grade: int | None = None) -> Lesson | None:
    module = module_of(lesson_id)
    if module is None:
        return None
    found = False
    for lesson in module.lessons:
        if lesson.id == lesson_id:
            found = True
            continue
        if found and (grade is None or grade in lesson.grades):
            return lesson
    return None


def first_lesson(grade: int | None = None) -> tuple[Module, Lesson]:
    for module in MODULES:
        for lesson in module.lessons:
            if grade is None or grade in lesson.grades:
                return module, lesson
    return MODULES[0], MODULES[0].lessons[0]


def public_problem(problem: Problem) -> dict:
    data = {
        "id": problem.id,
        "prompt": problem.prompt,
        "kind": problem.kind,
        "hint": problem.hint,
    }
    if problem.kind == "choice":
        data["choices"] = [{"id": choice_id, "label": label} for choice_id, label in problem.choices]
    return data


def is_correct(problem: Problem, given: str) -> bool:
    return normalize(given) in set(problem.answers)


def problem_in(lesson: Lesson, problem_id: str) -> Problem | None:
    for problem in lesson.problems:
        if problem.id == problem_id:
            return problem
    return None


def stats() -> dict[str, int]:
    lessons = sum(len(module.lessons) for module in MODULES)
    problems = sum(len(lesson.problems) for module in MODULES for lesson in module.lessons)
    return {"modules": len(MODULES), "lessons": lessons, "problems": problems}


def repertorio(grade: int | None = None) -> dict:
    modules = []
    for module in MODULES:
        lessons = visible_lessons(module, grade)
        modules.append(
            {
                "slug": module.slug,
                "number": module.number,
                "title": module.title,
                "blurb": module.blurb,
                "tint": module.tint,
                "grade_label": module.grade_label,
                "lesson_count": len(lessons),
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "summary": lesson.summary,
                        "grades": list(lesson.grades),
                        "grade_label": lesson.grade_label,
                        "problem_count": len(lesson.problems),
                    }
                    for lesson in lessons
                ],
            }
        )
    return {"name": "MatiLab", "grades": list(GRADES), "modules": modules}
