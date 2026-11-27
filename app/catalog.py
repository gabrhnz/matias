"""Repertorio de MatiLab: cuatro módulos para 3.º a 6.º grado."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.visuals import apply_figures

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
    scene: dict | None = None


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
    example_scene: dict | None = None

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
                if module.slug in {"fracciones", "geometria"} and problem.scene is None:
                    raise ValueError(f"{problem.id} necesita una figura")
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
                "Empieza por la derecha, las unidades. Si juntas 10 o más, anota lo que sobra de 10 y lleva 1 al número de al lado, las decenas.",
                "18 + 5",
                "8 + 5 = 13. Escribes 3 y llevas 1. 1 + 1 = 2. El resultado es 23.",
                [
                    C("¿Cuánto es 27 + 15?", ["32", "42", "41", "52"], "42", "7 + 5 = 12. Escribes 2 y llevas 1. 2 + 1 + 1 = 4. Resultado: 42.", "Suma primero las de la derecha. Si pasan de 9, lleva 1."),
                    C("¿Cuánto es 46 + 38?", ["74", "84", "714", "85"], "84", "6 + 8 = 14. Escribes 4 y llevas 1. 4 + 3 + 1 = 8. Resultado: 84.", "Suma 6 + 8. Si da 10 o más, llevas 1."),
                    N("¿Cuánto es 109 + 26?", "135", "9 + 6 = 15. Escribes 5 y llevas 1. 0 + 2 + 1 = 3. El 1 de las centenas se queda. Resultado: 135.", "Empieza por 9 + 6, las unidades."),
                    C("Ana tiene 48 láminas y le regalan 17. ¿Cuántas tiene ahora?", ["55", "65", "61", "75"], "65", "8 + 7 = 15. Escribes 5 y llevas 1. 4 + 1 + 1 = 6. Ana tiene 65 láminas.", "Junta 48 y 17. No olvides lo que llevas."),
                ],
            ),
            _lesson(
                "restar-con-prestado",
                "Restar pidiendo prestado",
                "Si una cifra no alcanza, pides 1 a la cifra de la izquierda.",
                (3,),
                "Si el número de arriba es más chiquito y no alcanza, pídele 1 al de la izquierda. Ese 1 se vuelve 10 y ya puedes restar.",
                "32 − 15",
                "2 no alcanza para quitar 5. Pides 1 a las decenas: quedan 2 decenas y 12 unidades. 12 − 5 = 7 y 2 − 1 = 1. Resultado: 17.",
                [
                    C("¿Cuánto es 42 − 17?", ["25", "35", "29", "15"], "25", "2 no alcanza. Pides prestado: 12 − 7 = 5 y 3 − 1 = 2. Resultado: 25.", "Mira primero las unidades. Si no alcanzan, pide prestado."),
                    C("¿Cuánto es 70 − 26?", ["44", "56", "54", "46"], "44", "0 no alcanza. La decena se convierte en 10. 10 − 6 = 4 y 6 − 2 = 4. Resultado: 44.", "El 0 no alcanza. Pídele 1 al número de al lado."),
                    N("¿Cuánto es 103 − 45?", "58", "103 − 45 = 58. Puedes comprobarlo sumando: 58 + 45 = 103.", "Empieza por las unidades. Si el 3 no alcanza para quitar 5, pide prestado."),
                    C("Tenías 50 monedas de juguete y gastaste 18. ¿Cuántas te quedan?", ["32", "42", "28", "48"], "32", "50 − 18. El 0 pide prestado: 10 − 8 = 2 y 4 − 1 = 3. Quedan 32.", "Es quitar: 50 − 18. El 0 necesita un préstamo."),
                ],
            ),
            _lesson(
                "tablas-de-multiplicar",
                "Las tablas de multiplicar",
                "Multiplicar es sumar el mismo número varias veces.",
                (3, 4),
                "4 × 3 quiere decir 4 + 4 + 4: tres grupos de 4. Da igual el orden. 4 × 3 es lo mismo que 3 × 4.",
                "4 × 3",
                "Tres grupos de 4 son 12. También puedes pensar 4 + 4 + 4.",
                [
                    C("¿Cuánto es 6 × 7?", ["36", "42", "48", "13"], "42", "6 × 7 = 42. Es la tabla del 6 o la del 7.", "Piensa en 7 grupos de 6, o cuenta la tabla del 6."),
                    C("¿Cuánto es 8 × 4?", ["24", "32", "36", "12"], "32", "8 × 4 = 32. Cuatro grupos de 8.", "Suma 8 cuatro veces: 8 + 8 + 8 + 8."),
                    C("¿Cuánto es 9 × 5?", ["45", "40", "14", "95"], "45", "9 × 5 = 45. Cinco grupos de 9.", "En la tabla del 5, los resultados terminan en 0 o en 5."),
                    C("Hay 3 cajas con 8 lápices cada una. ¿Cuántos lápices hay?", ["11", "24", "16", "32"], "24", "3 × 8 = 24 lápices.", "Son 3 cajas iguales. Multiplica 3 × 8."),
                ],
            ),
            _lesson(
                "multiplicar-dos-cifras",
                "Multiplicar por una cifra",
                "Multiplicas las unidades y después las decenas.",
                (4,),
                "Parte el número. En 23 × 3, primero 3 × 3 = 9. Después 20 × 3 = 60, porque 2 decenas son 20. Junta 60 + 9 = 69.",
                "12 × 4",
                "4 × 2 = 8 unidades. 4 × 1 decena = 4 decenas. Resultado: 48.",
                [
                    C("¿Cuánto es 12 × 4?", ["16", "48", "46", "412"], "48", "4 × 2 = 8 y 4 × 10 = 40. 40 + 8 = 48.", "Separa 12 en 10 y 2. Multiplica cada parte por 4."),
                    C("¿Cuánto es 23 × 3?", ["26", "69", "66", "29"], "69", "3 × 3 = 9 y 3 × 20 = 60. 60 + 9 = 69.", "23 es 20 + 3. Multiplica cada uno por 3 y junta."),
                    N("¿Cuánto es 15 × 6?", "90", "6 × 5 = 30, llevas 3. 6 × 1 = 6, más 3 son 9. Resultado: 90.", "Haz 10 × 6 y 5 × 6, y suma los dos resultados."),
                    C("Cinco paquetes traen 14 galletas cada uno. ¿Cuántas galletas hay?", ["19", "70", "64", "54"], "70", "5 × 14 = 70. 5 × 10 = 50 y 5 × 4 = 20.", "Hay 5 paquetes iguales. Multiplica 5 × 14."),
                ],
            ),
            _lesson(
                "dividir-en-partes",
                "Dividir en partes iguales",
                "Dividir es repartir en grupos del mismo tamaño.",
                (4,),
                "Dividir es repartir en grupos iguales. 24 ÷ 6 pregunta: ¿cuántos grupos de 6 caben en 24? Como 6 × 4 = 24, caben 4.",
                "18 ÷ 3",
                "3 × 6 = 18, así que 18 ÷ 3 = 6. Cada parte queda con 6.",
                [
                    C("¿Cuánto es 24 ÷ 6?", ["4", "6", "18", "3"], "4", "6 × 4 = 24, así que 24 ÷ 6 = 4.", "Busca un número que, multiplicado por 6, dé 24."),
                    C("¿Cuánto es 36 ÷ 4?", ["8", "9", "6", "32"], "9", "4 × 9 = 36. El cociente es 9.", "Usa la tabla del 4: ¿4 por cuánto da 36?"),
                    N("¿Cuánto es 45 ÷ 9?", "5", "9 × 5 = 45. Por eso 45 ÷ 9 = 5.", "Pregunta: ¿cuántas veces cabe el 9 en 45?"),
                    C("Hay 18 caramelos para 3 amigos, en partes iguales. ¿Cuántos recibe cada uno?", ["6", "15", "21", "9"], "6", "18 ÷ 3 = 6. Cada amigo recibe 6 caramelos.", "Repartir en partes iguales es dividir: 18 entre 3."),
                ],
            ),
            _lesson(
                "division-con-residuo",
                "División con residuo",
                "A veces la división no es exacta y sobra una cantidad.",
                (4, 5),
                "A veces no cabe exacto. En 17 ÷ 5 caben 3 grupos, porque 5 × 3 = 15. Sobran 2. El 3 es cuántas veces cabe. El 2 es lo que sobra: el residuo.",
                "17 ÷ 5",
                "Caben 3 grupos de 5 y sobran 2. Cociente 3, residuo 2.",
                [
                    C("En 17 ÷ 5, ¿cuánto sobra?", ["1", "2", "3", "5"], "2", "5 × 3 = 15 y 17 − 15 = 2. El residuo es 2.", "Haz grupos de 5 sin pasarte de 17. Lo que quede es lo que sobra."),
                    C("¿Cuál es el cociente de 23 ÷ 4?", ["5", "3", "6", "4"], "5", "4 × 5 = 20. Cabe 5 veces y sobran 3. El cociente es 5.", "Te piden cuántas veces cabe, no lo que sobra."),
                    N("¿Cuánto sobra al dividir 20 ÷ 6?", "2", "6 × 3 = 18 y 20 − 18 = 2. El residuo es 2.", "Busca 6 por un número que no pase de 20. Luego mira lo que queda."),
                    C("Tienes 31 stickers y los pegas de 7 en 7. ¿Cuántos sobran?", ["3", "4", "1", "7"], "3", "7 × 4 = 28 y 31 − 28 = 3. Sobran 3 stickers.", "Arma grupos de 7 sin pasarte de 31. Cuenta los que no entran."),
                ],
            ),
            _lesson(
                "orden-de-operaciones",
                "Orden de las operaciones",
                "Primero paréntesis, después × y ÷, y al final + y −.",
                (5,),
                "No todo se hace de izquierda a derecha. Primero lo que está entre paréntesis ( ). Después las multiplicaciones y las divisiones. Al final, las sumas y las restas.",
                "20 − 6 ÷ 2",
                "Primero 6 ÷ 2 = 3. Luego 20 − 3 = 17.",
                [
                    C("¿Cuánto es 3 + 4 × 2?", ["14", "11", "9", "24"], "11", "Primero 4 × 2 = 8. Después 3 + 8 = 11.", "Aquí no sumes primero. La multiplicación va antes."),
                    C("¿Cuánto es (3 + 4) × 2?", ["14", "11", "10", "9"], "14", "El paréntesis se resuelve primero: 3 + 4 = 7. Luego 7 × 2 = 14.", "Lo que está dentro de ( ) se hace primero."),
                    N("¿Cuánto es 20 − 6 ÷ 2?", "17", "6 ÷ 2 = 3 y 20 − 3 = 17.", "Primero divide. La resta va después."),
                    N("¿Cuánto es 2 × (8 − 3) + 1?", "11", "8 − 3 = 5. Luego 2 × 5 = 10. Al final 10 + 1 = 11.", "Empieza por lo que está dentro del paréntesis."),
                ],
            ),
            _lesson(
                "problemas-de-cada-dia",
                "Problemas de cada día",
                "Lees el problema, eliges la operación y compruebas si el resultado tiene sentido.",
                (5, 6),
                "Lee con calma y pregunta: ¿estoy juntando, quitando, haciendo grupos iguales o repartiendo? Haz esa cuenta y mira si el resultado tiene sentido.",
                "Un bus lleva 36 niños y cada fila tiene 4 asientos. ¿Cuántas filas se ocupan?",
                "Se reparten 36 en grupos de 4. 36 ÷ 4 = 9 filas.",
                [
                    C("Un bus lleva 36 niños. Cada fila tiene 4 asientos. ¿Cuántas filas se ocupan?", ["9", "32", "40", "8"], "9", "36 ÷ 4 = 9 filas.", "Los niños se sientan en filas iguales. Eso es dividir."),
                    N("Compras 3 paquetes de 12 crayones y regalas 5. ¿Cuántos te quedan?", "31", "3 × 12 = 36 y 36 − 5 = 31.", "Primero junta los 3 paquetes. Después quita los que regalas."),
                    N("Cada entrada cuesta 8. Compras 4 y pagas con 50. ¿Cuánto te devuelven?", "18", "4 × 8 = 32. 50 − 32 = 18.", "Calcula cuánto cuestan las 4 entradas. Luego réstalo de 50."),
                    N("Durante 5 días haces 6 ejercicios por día. Ya hiciste 11. ¿Cuántos te faltan?", "19", "5 × 6 = 30 ejercicios en total. 30 − 11 = 19.", "Primero calcula cuántos ejercicios son en total. Después quita los que ya hiciste."),
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
                "Una fracción parte algo en pedazos iguales. El número de abajo dice en cuántos pedazos. El de arriba dice cuántos tomas. En 3/8 hay 8 pedazos y tomas 3.",
                "Una pizza se corta en 4 partes iguales y comes 1.",
                "Comes 1 de 4 partes iguales. La fracción es 1/4.",
                [
                    C("Una pizza se corta en 4 partes iguales y comes 1. ¿Qué fracción comiste?", ["1/2", "1/4", "4/1", "3/4"], "1/4", "Tomaste 1 parte de 4 iguales: 1/4.", "Abajo va en cuántas partes iguales se cortó. Arriba, cuántas comiste."),
                    C("Un chocolate se parte en 8 y tomas 3. ¿Qué fracción tomas?", ["3/8", "8/3", "3/5", "5/8"], "3/8", "3 partes de 8 iguales: 3/8.", "Tomas 3 pedazos de 8. El 3 va arriba y el 8 abajo."),
                    C("¿Qué número dice en cuántas partes iguales se divide el entero?", ["El numerador", "El denominador", "El residuo", "El cociente"], "El denominador", "El denominador, el número de abajo, cuenta las partes iguales.", "Es el número que está debajo de la raya."),
                    C("Pintas 2 de 6 partes iguales. ¿Qué fracción pintaste?", ["6/2", "2/6", "2/4", "4/6"], "2/6", "Pintaste 2 partes de 6: 2/6.", "Las partes pintadas van arriba. Todas las partes van abajo."),
                ],
            ),
            _lesson(
                "leer-fracciones",
                "Leer y escribir fracciones",
                "Cada denominador tiene un nombre: medios, tercios, cuartos, octavos.",
                (3, 4),
                "El número de abajo le pone el nombre. 2 se dice medios, 3 tercios, 4 cuartos y 8 octavos. 1/2 se lee «un medio». 2/3 se lee «dos tercios».",
                "3/4",
                "Se lee tres cuartos: tres partes de cuatro iguales.",
                [
                    C("¿Cómo se lee 2/3?", ["Dos medios", "Dos tercios", "Tres medios", "Tres cuartos"], "Dos tercios", "El denominador 3 se llama tercios. 2/3 es dos tercios.", "Si abajo hay 3, el nombre es tercios."),
                    C("¿Cómo se lee 1/2?", ["Un cuarto", "Un medio", "Dos medios", "Un tercio"], "Un medio", "1/2 es un medio: una de dos partes iguales.", "Partir en 2 es hacer mitades. 1/2 es un medio."),
                    C("¿Cómo se lee 3/4?", ["Tres medios", "Cuatro tercios", "Tres cuartos", "Tres octavos"], "Tres cuartos", "El 4 se llama cuartos. 3/4 es tres cuartos.", "Abajo hay 4: se llaman cuartos. Como una pizza en 4."),
                    C("¿Cómo se lee 5/8?", ["Cinco octavos", "Ocho quintos", "Cinco cuartos", "Cinco medios"], "Cinco octavos", "El denominador 8 se llama octavos. 5/8 es cinco octavos.", "Abajo hay 8 partes iguales. Se llaman octavos."),
                ],
            ),
            _lesson(
                "fracciones-equivalentes",
                "Fracciones equivalentes",
                "Dos fracciones son equivalentes cuando nombran la misma cantidad.",
                (4,),
                "Dos fracciones pueden verse distintas y valer lo mismo. 1/2 y 2/4 son la misma cantidad. Si multiplicas o divides el de arriba y el de abajo por el mismo número, la fracción no cambia.",
                "1/2 y 2/4",
                "2 ÷ 2 = 1 y 4 ÷ 2 = 2. Por eso 2/4 = 1/2. Son equivalentes.",
                [
                    C("¿Cuál es equivalente a 1/2?", ["2/4", "2/3", "1/3", "3/4"], "2/4", "1 × 2 = 2 y 2 × 2 = 4. 1/2 = 2/4.", "Multiplica el 1 y el 2 por el mismo número: por 2."),
                    C("¿Cuál es equivalente a 1/3?", ["2/6", "2/3", "3/6", "1/6"], "2/6", "1 × 2 = 2 y 3 × 2 = 6. 1/3 = 2/6.", "Multiplica arriba y abajo por el mismo número."),
                    C("¿2/4 y 1/2 son equivalentes?", ["Sí", "No"], "Sí", "2/4 simplificada, dividiendo entre 2, es 1/2. Nombran la misma cantidad.", "Dibuja una mitad y otra figura en 4 partes con 2 pintadas. ¿Se ven igual?"),
                    C("¿Cuál es equivalente a 3/6?", ["1/2", "2/3", "1/3", "3/3"], "1/2", "3 ÷ 3 = 1 y 6 ÷ 3 = 2. 3/6 = 1/2.", "Divide el de arriba y el de abajo entre 3."),
                ],
            ),
            _lesson(
                "comparar-fracciones",
                "Comparar fracciones",
                "Con el mismo entero, puedes decir cuál fracción es mayor.",
                (4, 5),
                "Para comparar, mira el mismo entero. Si el de abajo es igual, gana quien tiene más arriba: 5/8 es más que 3/8. Si arriba hay 1, gana el de abajo más chiquito: 1/2 es más que 1/4, porque cada pedazo es más grande.",
                "¿Qué es mayor, 1/2 o 1/4?",
                "Un medio es más grande que un cuarto. 1/2 se lleva la mitad del entero y 1/4 solo una de cuatro partes.",
                [
                    C("¿Qué es mayor?", ["1/2", "1/4", "Son iguales"], "1/2", "La mitad es más grande que un cuarto del mismo entero.", "Si partes en más pedazos, cada pedazo queda más chiquito."),
                    C("¿Qué es mayor, 2/3 o 1/3?", ["2/3", "1/3", "Son iguales"], "2/3", "El denominador es el mismo. 2 partes son más que 1 parte.", "Los pedazos son del mismo tamaño. Mira quién toma más."),
                    C("¿Qué pasa con 1/2 y 2/4?", ["1/2 es mayor", "2/4 es mayor", "Son iguales"], "Son iguales", "2/4 es equivalente a 1/2. No hay una mayor.", "Divide 2 y 4 entre 2. ¿Queda igual que 1/2?"),
                    C("¿Qué es mayor, 3/8 o 5/8?", ["3/8", "5/8", "Son iguales"], "5/8", "Las partes son octavos. Cinco octavos son más que tres octavos.", "Abajo los dos tienen 8. Compara solo los de arriba."),
                ],
            ),
            _lesson(
                "sumar-fracciones",
                "Sumar fracciones",
                "Si el denominador es el mismo, sumas los numeradores y lo dejas igual.",
                (4, 5),
                "Si abajo está el mismo número, suma solo los de arriba. 1/5 + 2/5 = 3/5. El 5 se queda: los pedazos siguen siendo quintos.",
                "1/5 + 2/5",
                "1 + 2 = 3 numeradores. El denominador sigue siendo 5. Resultado: 3/5.",
                [
                    C("¿Cuánto es 1/5 + 2/5?", ["3/5", "3/10", "2/5", "1/5"], "3/5", "1 + 2 = 3 y el denominador no cambia: 3/5.", "Suma solo los números de arriba. El de abajo se queda."),
                    C("¿Cuánto es 2/8 + 3/8?", ["5/8", "5/16", "6/8", "1/8"], "5/8", "2 + 3 = 5. Los octavos se quedan: 5/8.", "Abajo los dos son 8. Suma 2 + 3 y deja el 8."),
                    N("¿Cuánto es 1/4 + 1/4? Puedes simplificar.", ("2/4", "1/2"), "1 + 1 = 2, así que es 2/4. Y 2/4 equivale a 1/2.", "Suma los de arriba. Si puedes, divide arriba y abajo entre 2."),
                    N("¿Cuánto es 3/10 + 4/10?", "7/10", "3 + 4 = 7. El resultado es 7/10.", "Abajo hay 10 en las dos. No sumes esos 10."),
                ],
            ),
            _lesson(
                "restar-fracciones",
                "Restar fracciones",
                "Con el mismo denominador, restas los numeradores.",
                (5,),
                "Si abajo está el mismo número, resta solo los de arriba. 4/6 − 1/6 = 3/6. Quitas pedazos del mismo tamaño y el de abajo se queda.",
                "5/7 − 2/7",
                "5 − 2 = 3. Quedan 3/7.",
                [
                    N("¿Cuánto es 4/6 − 1/6? Puedes simplificar.", ("3/6", "1/2"), "4 − 1 = 3, así que es 3/6. Eso equivale a 1/2.", "Resta solo los de arriba. El 6 se queda."),
                    N("¿Cuánto es 5/7 − 2/7?", "3/7", "5 − 2 = 3. El resultado es 3/7.", "El 7 de abajo no cambia. Resta 5 − 2."),
                    N("¿Cuánto es 3/4 − 1/4? Puedes simplificar.", ("2/4", "1/2"), "3 − 1 = 2. Queda 2/4, que es 1/2.", "Quita 1 pedazo de 3 pedazos del mismo tamaño."),
                    C("Tenías 7/8 de un litro y usaste 2/8. ¿Cuánto queda?", ["5/8", "9/8", "5/16", "2/8"], "5/8", "7 − 2 = 5. Quedan 5/8 de litro.", "Las dos cantidades son octavos. Resta los de arriba."),
                ],
            ),
            _lesson(
                "fraccion-de-una-cantidad",
                "Fracción de una cantidad",
                "Para hallar una fracción de un número, divides y después multiplicas si hace falta.",
                (5, 6),
                "Para sacar una parte de un número, primero reparte. 1/4 de 20 es 20 ÷ 4 = 5. Si el de arriba no es 1, después multiplicas: 2/3 de 9 es 9 ÷ 3 = 3, y 3 × 2 = 6.",
                "1/2 de 10",
                "La mitad de 10 es 10 ÷ 2 = 5.",
                [
                    C("¿Cuánto es 1/2 de 10?", ["2", "5", "8", "20"], "5", "10 ÷ 2 = 5. Un medio de 10 es 5.", "La mitad es dividir entre 2."),
                    C("¿Cuánto es 1/4 de 20?", ["4", "5", "10", "16"], "5", "20 ÷ 4 = 5. Un cuarto de 20 es 5.", "Parte 20 en 4 grupos iguales."),
                    N("¿Cuánto es 2/3 de 9?", "6", "9 ÷ 3 = 3 y 3 × 2 = 6.", "Primero parte 9 en 3. Después toma 2 de esas partes."),
                    N("¿Cuánto es 3/5 de 15?", "9", "15 ÷ 5 = 3 y 3 × 3 = 9.", "Primero divide entre 5. Después multiplica por 3."),
                ],
            ),
            _lesson(
                "numeros-mixtos",
                "Números mixtos",
                "Un número mixto junta enteros y una fracción. Una fracción mayor que 1 se puede escribir así.",
                (6,),
                "A veces la fracción pasa de un entero. 4/4 es 1 entero. En 7/4 caben 4/4 y sobran 3/4. Eso se escribe 1 entero y 3/4.",
                "7/4",
                "4/4 forman 1 entero y sobran 3/4. Se escribe 1 3/4.",
                [
                    N("En 7/4, ¿cuántos enteros completos hay?", "1", "4/4 es un entero y sobran 3 cuartos. Hay 1 entero.", "¿Cuántas veces cabe el 4 en el 7? Eso son los enteros."),
                    N("¿Qué fracción impropia es 1 entero y 1/2?", "3/2", "1 entero es 2/2. Más 1/2 da 3/2.", "1 entero son 2 medios. Súmale el medio que ya tienes."),
                    N("De 11/3, después de sacar los enteros, ¿cuántos tercios sobran?", "2", "3 × 3 = 9, así que hay 3 enteros. 11 − 9 = 2. Sobran 2/3.", "Divide 11 entre 3 y mira lo que sobra. Eso son los tercios que quedan."),
                    N("Escribe 2 enteros y 1/4 como fracción impropia.", "9/4", "2 enteros son 8/4. Más 1/4 da 9/4.", "Cada entero son 4 cuartos. Calcula los de 2 enteros y suma el cuarto."),
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
                "El triángulo tiene 3 lados. El cuadrado tiene 4 lados iguales. El rectángulo también tiene 4, pero solo los de enfrente miden igual. El círculo es redondo y no tiene lados rectos.",
                "Una figura de 3 lados rectos",
                "Es un triángulo.",
                [
                    C("¿Cómo se llama la figura de 3 lados?", ["Cuadrado", "Triángulo", "Círculo", "Rectángulo"], "Triángulo", "Tres lados rectos forman un triángulo.", "Cuenta los lados rectos."),
                    C("¿Qué figura tiene 4 lados iguales y 4 esquinas iguales?", ["Rectángulo", "Triángulo", "Cuadrado", "Círculo"], "Cuadrado", "El cuadrado tiene los cuatro lados de la misma longitud.", "Tiene 4 lados y los 4 miden lo mismo."),
                    C("¿Qué figura no tiene lados rectos?", ["Triángulo", "Cuadrado", "Rectángulo", "Círculo"], "Círculo", "El círculo es una curva cerrada. No tiene lados ni vértices.", "Piensa en una moneda: es redonda."),
                    C("Tiene 4 lados y los opuestos son iguales, pero no todos miden lo mismo. ¿Qué es?", ["Cuadrado", "Rectángulo", "Triángulo", "Círculo"], "Rectángulo", "En el rectángulo, los lados de enfrente coinciden y no todos son iguales, como en el cuadrado.", "Una puerta suele tener esta forma: 4 lados, y los de enfrente miden igual."),
                ],
            ),
            _lesson(
                "lados-y-vertices",
                "Lados y vértices",
                "Un vértice es la esquina donde se juntan dos lados.",
                (3, 4),
                "El lado es cada línea del borde. El vértice es la esquina, donde se juntan dos lados. Un triángulo tiene 3 lados y 3 esquinas. Un cuadrado tiene 4 y 4.",
                "Un triángulo",
                "Tiene 3 lados y 3 vértices.",
                [
                    C("¿Cuántos vértices tiene un triángulo?", ["2", "3", "4", "6"], "3", "Cada esquina es un vértice. El triángulo tiene 3.", "Cuenta las puntas, las esquinas."),
                    C("¿Cuántos lados tiene un cuadrado?", ["3", "4", "5", "8"], "4", "El cuadrado tiene 4 lados.", "Sigue el borde con el dedo y cuenta las líneas."),
                    N("¿Cuántos lados tiene un pentágono?", "5", "Un pentágono tiene 5 lados.", "Penta quiere decir cinco. Cuenta como los dedos de una mano."),
                    C("¿Cuántos vértices tiene un rectángulo?", ["3", "4", "6", "8"], "4", "El rectángulo tiene 4 esquinas, así que tiene 4 vértices.", "Las esquinas son los vértices. Cuéntalas."),
                ],
            ),
            _lesson(
                "perimetro",
                "Perímetro",
                "El perímetro es la suma de todos los lados: el borde de la figura.",
                (4,),
                "El perímetro es el borde, como una cerca alrededor. No cuentes el espacio de adentro. Suma todos los lados. Un cuadrado de lado 5 mide 5 + 5 + 5 + 5 = 20.",
                "Cuadrado de lado 5",
                "4 × 5 = 20. El perímetro mide 20.",
                [
                    C("Un cuadrado tiene lado 5. ¿Cuál es su perímetro?", ["10", "20", "25", "15"], "20", "Hay 4 lados de 5. 4 × 5 = 20.", "Suma los 4 lados del borde. No cuentes el espacio de adentro."),
                    C("Un rectángulo mide 6 de largo y 3 de ancho. ¿Cuál es su perímetro?", ["18", "9", "24", "12"], "18", "6 + 3 + 6 + 3 = 18. También 2 × (6 + 3) = 18.", "Hay 2 lados largos y 2 lados cortos. Súmalos todos."),
                    N("Un triángulo tiene lados 4, 4 y 3. ¿Cuál es su perímetro?", "11", "4 + 4 + 3 = 11.", "Suma los tres lados."),
                    N("Un patio rectangular mide 8 m por 2 m. ¿Cuántos metros de cerca lo rodean?", "20", "El perímetro es 8 + 2 + 8 + 2 = 20 metros.", "La cerca va por el borde. Suma los cuatro lados."),
                ],
            ),
            _lesson(
                "area-del-rectangulo",
                "Área del rectángulo",
                "El área dice cuánta superficie cubre la figura.",
                (4, 5),
                "El área es la superficie, lo que cabe adentro. En un rectángulo se calcula con largo × ancho. El cuadrado es un rectángulo especial: lado × lado.",
                "Rectángulo de 4 por 3",
                "4 × 3 = 12. El área es 12 unidades cuadradas.",
                [
                    C("Un rectángulo mide 4 por 3. ¿Cuál es su área?", ["7", "12", "14", "24"], "12", "4 × 3 = 12 unidades cuadradas.", "Multiplica el largo por el ancho."),
                    C("¿Cuál es el área de un rectángulo de 7 por 2?", ["9", "14", "18", "28"], "14", "7 × 2 = 14.", "Multiplica 7 por 2."),
                    N("Un cuadrado tiene lado 6. ¿Cuál es su área?", "36", "6 × 6 = 36.", "En el cuadrado, los dos lados que multiplicas son iguales."),
                    N("Una huerta mide 5 m por 4 m. ¿Cuál es su área?", "20", "5 × 4 = 20 metros cuadrados.", "Multiplica 5 por 4. Eso son metros cuadrados, el espacio de la huerta."),
                ],
            ),
            _lesson(
                "area-del-triangulo",
                "Área del triángulo",
                "El área de un triángulo es base × altura ÷ 2.",
                (5,),
                "Un triángulo es como la mitad de un rectángulo con la misma base y la misma altura. Por eso haces base × altura y después divides entre 2.",
                "Base 6 y altura 4",
                "6 × 4 = 24. 24 ÷ 2 = 12. El área es 12.",
                [
                    N("Base 6 y altura 4. ¿Cuál es el área?", "12", "6 × 4 = 24 y 24 ÷ 2 = 12.", "Multiplica la base por la altura y después parte el resultado a la mitad."),
                    N("Base 10 y altura 3. ¿Cuál es el área?", "15", "10 × 3 = 30 y 30 ÷ 2 = 15.", "Primero multiplica. No te olvides de dividir entre 2."),
                    N("Base 8 y altura 5. ¿Cuál es el área?", "20", "8 × 5 = 40 y 40 ÷ 2 = 20.", "La altura es la línea que baja derecha hasta la base. Multiplica y divide entre 2."),
                    N("Base 7 y altura 2. ¿Cuál es el área?", "7", "7 × 2 = 14 y 14 ÷ 2 = 7.", "Multiplica base por altura y divide ese resultado entre 2."),
                ],
            ),
            _lesson(
                "simetria",
                "Simetría",
                "Un eje de simetría parte la figura en dos mitades que coinciden al doblarla.",
                (5,),
                "El eje es una línea para doblar. Si al doblar una mitad cae justo sobre la otra, hay simetría. Un cuadrado se puede doblar de varias formas. Un círculo, por cualquier línea que pase por el centro.",
                "La letra A mayúscula",
                "Tiene un eje vertical: la mitad izquierda y la derecha coinciden.",
                [
                    C("¿El cuadrado tiene eje de simetría?", ["Sí", "No"], "Sí", "Puedes doblarlo por la mitad vertical, horizontal o por las diagonales.", "Imagina que doblas un papel cuadrado por la mitad. ¿Coinciden los dos lados?"),
                    C("¿La letra A mayúscula tiene un eje vertical?", ["Sí", "No"], "Sí", "La A queda igual a los dos lados de una línea vertical por el centro.", "Pon un espejo en el medio de la A. ¿Se ve igual a los dos lados?"),
                    C("¿Cuántos ejes de simetría tiene un círculo?", ["0", "1", "4", "Infinitos"], "Infinitos", "Cualquier diámetro parte el círculo en dos mitades iguales. Hay infinitos diámetros.", "Cualquier línea que pase por el centro lo parte en dos mitades iguales. Hay muchísimas."),
                    C("Un corazón típico, ¿cuántos ejes de simetría tiene?", ["0", "1", "2", "4"], "1", "Solo el eje vertical deja las dos mitades iguales.", "Solo la línea de arriba abajo deja las dos mitades iguales. La de lado a lado, no."),
                ],
            ),
            _lesson(
                "angulos",
                "Ángulos",
                "Un ángulo mide la abertura entre dos lados que se juntan.",
                (5, 6),
                "Un ángulo es qué tan abierto está el espacio entre dos lados. La esquina de una hoja mide 90 grados: es un ángulo recto. Si está más cerrado, es agudo. Si está más abierto que la esquina, pero no llega a una línea, es obtuso.",
                "La esquina de una hoja de papel",
                "Es un ángulo recto. Mide 90 grados.",
                [
                    C("¿Cuánto mide un ángulo recto?", ["45 grados", "90 grados", "180 grados", "60 grados"], "90 grados", "El ángulo recto mide 90 grados.", "Es la misma abertura que la esquina de tu cuaderno."),
                    C("Un ángulo menor que 90 grados es…", ["Recto", "Agudo", "Obtuso", "Llano"], "Agudo", "Si la abertura es más cerrada que la esquina de la hoja, el ángulo es agudo.", "Agudo es más cerrado, más chiquito que la esquina de la hoja."),
                    C("Un ángulo mayor que 90 y menor que 180 grados es…", ["Agudo", "Recto", "Obtuso", "Completo"], "Obtuso", "Está más abierto que un recto, pero no llega a ser una línea recta.", "Está más abierto que la esquina de la hoja, pero no es una línea recta."),
                    C("¿Qué ángulo es la esquina de una hoja de papel?", ["Agudo", "Recto", "Obtuso", "Llano"], "Recto", "Las esquinas de la hoja son ángulos rectos.", "Las esquinas de la hoja miden 90 grados."),
                ],
            ),
            _lesson(
                "volumen-de-una-caja",
                "Volumen de una caja",
                "El volumen dice cuánto espacio ocupa un cuerpo, o cuánto cabe dentro.",
                (6,),
                "El volumen es cuánto espacio ocupa una caja, o cuánto cabe dentro. Se multiplica largo × ancho × alto. En un cubo, las tres medidas son iguales.",
                "Caja de 2 × 3 × 4",
                "2 × 3 = 6 y 6 × 4 = 24. El volumen es 24 unidades cúbicas.",
                [
                    N("Una caja mide 2 × 3 × 4. ¿Cuál es su volumen?", "24", "2 × 3 × 4 = 24.", "Multiplica las tres medidas: largo, ancho y alto."),
                    N("Un cubo tiene lado 3. ¿Cuál es su volumen?", "27", "3 × 3 × 3 = 27.", "En el cubo, largo, ancho y alto son el mismo número. Multiplícalo tres veces."),
                    N("Una caja mide 5 × 2 × 2. ¿Cuál es su volumen?", "20", "5 × 2 × 2 = 20.", "Multiplica 5 × 2 y ese resultado por 2 otra vez."),
                    N("Una caja mide 10 × 4 × 3. ¿Cuál es su volumen?", "120", "10 × 4 = 40 y 40 × 3 = 120.", "Multiplica de dos en dos: primero dos medidas y luego la que falta."),
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
                "Un patrón es una regla que se repite. Cuando la descubres, ya sabes qué sigue. En 2, 4, 6, 8 la regla es sumar 2. En rojo, azul, rojo, azul, los colores se turnan.",
                "2, 4, 6, 8, …",
                "Se suma 2 cada vez. Sigue el 10.",
                [
                    C("¿Qué sigue? 2, 4, 6, 8, …", ["9", "10", "12", "16"], "10", "La regla es +2. Después de 8 viene 10.", "Mira cuánto sube de un número al siguiente. Haz lo mismo otra vez."),
                    C("¿Qué sigue? Rojo, azul, rojo, azul, …", ["Rojo", "Azul", "Verde", "Amarillo"], "Rojo", "Los colores se turnan. Después de azul vuelve el rojo.", "Se turnan: uno y después el otro. Toca el que sigue."),
                    C("¿Qué sigue? 5, 10, 15, 20, …", ["21", "25", "30", "22"], "25", "Cuenta de 5 en 5. Después de 20 viene 25.", "Cuenta de 5 en 5, como la tabla del 5."),
                    C("¿Qué sigue? Triángulo, círculo, triángulo, círculo, …", ["Círculo", "Triángulo", "Cuadrado", "Rectángulo"], "Triángulo", "Se alternan triángulo y círculo. Toca de nuevo el triángulo.", "Son dos figuras que se turnan. ¿Cuál toca ahora?"),
                ],
            ),
            _lesson(
                "que-sigue",
                "Qué sigue en la serie",
                "La regla puede sumar, restar o ir cambiando de a poco.",
                (3, 4),
                "La regla no siempre es sumar lo mismo. A veces se resta, a veces se duplica. En 2, 3, 5, 8, 12 los saltos son 1, 2, 3 y 4. El siguiente salto es 5.",
                "1, 2, 4, 8, …",
                "Cada número es el doble del anterior. Sigue el 16.",
                [
                    C("¿Qué sigue? 1, 2, 4, 8, …", ["10", "12", "16", "9"], "16", "Cada término se duplica. 8 × 2 = 16.", "Compara cada número con el de antes. ¿Se duplica?"),
                    C("¿Qué sigue? 20, 17, 14, 11, …", ["8", "9", "10", "7"], "8", "Se resta 3 cada vez. 11 − 3 = 8.", "La serie baja. Mira cuánto baja cada vez y hazlo otra vez."),
                    N("¿Qué sigue? 3, 6, 9, 12, …", "15", "Suma 3 cada vez. 12 + 3 = 15.", "Cuenta de 3 en 3."),
                    N("¿Qué sigue? 2, 3, 5, 8, 12, …", "17", "Las diferencias son 1, 2, 3 y 4. La siguiente es 5. 12 + 5 = 17.", "Los saltos van creciendo: 1, luego 2, luego 3. ¿Cuál sigue?"),
                ],
            ),
            _lesson(
                "verdadero-o-falso",
                "Verdadero o falso",
                "Lees una frase con calma y decides si siempre es cierta.",
                (4,),
                "Lee la frase despacio. Es verdadera si la cuenta está bien para cualquier número que pruebes. Es falsa si encuentras un ejemplo que no funciona.",
                "Si sumas 0 a un número, el número queda igual.",
                "Es verdadero. 7 + 0 = 7 y lo mismo pasa con cualquier número.",
                [
                    C("Si sumas 0 a un número, el número queda igual.", ["Verdadero", "Falso"], "Verdadero", "Sumar 0 no cambia la cantidad.", "Prueba con un número fácil, como 7 + 0."),
                    C("La mitad de 10 es 6.", ["Verdadero", "Falso"], "Falso", "La mitad de 10 es 5, no 6.", "Calcula la mitad de 10 y compárala con 6."),
                    C("Un triángulo tiene 4 vértices.", ["Verdadero", "Falso"], "Falso", "Un triángulo tiene 3 vértices.", "Cuenta las esquinas de un triángulo."),
                    C("2 × 5 es igual a 5 × 2.", ["Verdadero", "Falso"], "Verdadero", "Las dos cuentas dan 10. En la multiplicación, el orden no cambia el producto.", "Haz 2 × 5 y también 5 × 2. ¿Dan lo mismo?"),
                ],
            ),
            _lesson(
                "quien-es",
                "Deduce quién es",
                "Las pistas se leen juntas. Cada una quita una posibilidad.",
                (4, 5),
                "Lee las pistas juntas. Cada una quita a alguien. Anota quién va primero y quién va después. Cuando solo queda una persona, esa es la respuesta.",
                "María es más alta que Pedro. Pedro es más alto que Lucía.",
                "Lucía es más baja que Pedro y Pedro es más bajo que María. La más baja es Lucía.",
                [
                    C("María es más alta que Pedro. Pedro es más alto que Lucía. ¿Quién es la persona más baja?", ["María", "Pedro", "Lucía"], "Lucía", "Lucía es más baja que Pedro, y Pedro es más bajo que María.", "Ordénalos del más alto al más bajo."),
                    C("Ana llega antes que Luis. Luis llega antes que Sofía. ¿Quién llega primero?", ["Ana", "Luis", "Sofía"], "Ana", "Ana está delante de Luis y Luis delante de Sofía. Ana llega primero.", "Busca quién está delante de los otros dos."),
                    C("El pájaro va delante del gato y el gato va delante del perro. ¿Quién va primero?", ["El perro", "El gato", "El pájaro"], "El pájaro", "El pájaro está delante del gato, así que también está delante del perro.", "El pájaro va delante del gato, y el gato delante del perro."),
                    C("Los números son 2, 5 y 9. El mayor no es 5 y el menor no es 9. ¿Cuál está en el medio?", ["2", "5", "9"], "5", "El mayor es 9 y el menor es 2. En el medio queda 5.", "Ordénalos de menor a mayor: 2, 5 y 9."),
                ],
            ),
            _lesson(
                "clasificar",
                "Clasificar",
                "Agrupar es poner juntos los elementos que comparten una regla.",
                (5,),
                "Clasificar es juntar lo que se parece. Elige una regla clara: fruta o verdura, par o impar. Después cuenta solo el grupo que te piden.",
                "2, 3, 4, 6 y 9. ¿Cuántos son pares?",
                "Los pares son 2, 4 y 6. Hay 3.",
                [
                    C("Manzana, zanahoria, banana y brócoli. ¿Cuáles son frutas?", ["Manzana y banana", "Zanahoria y brócoli", "Manzana y zanahoria", "Las cuatro"], "Manzana y banana", "La manzana y la banana son frutas. La zanahoria y el brócoli son verduras.", "Separa las frutas de las verduras."),
                    N("En 2, 3, 4, 6 y 9, ¿cuántos números son pares?", "3", "2, 4 y 6 son pares. El 3 y el 9 no. Hay 3.", "Un número par termina en 0, 2, 4, 6 u 8."),
                    C("¿Cuál no pertenece a 3, 6, 9, 10?", ["3", "6", "9", "10"], "10", "3, 6 y 9 son múltiplos de 3. 10 no lo es.", "Mira qué tienen en común 3, 6 y 9. El que no cumpla esa regla sobra."),
                    C("Triángulo, cuadrado, círculo y rectángulo. ¿Cuál no tiene lados rectos?", ["Triángulo", "Cuadrado", "Círculo", "Rectángulo"], "Círculo", "El círculo no tiene lados rectos. Las otras tres figuras sí.", "¿Cuál de las cuatro es redonda y no tiene lados rectos?"),
                ],
            ),
            _lesson(
                "caminos",
                "Caminos y decisiones",
                "Cuentas las posibilidades sin saltarte ninguna y sin repetir.",
                (5, 6),
                "Cuenta los caminos sin saltarte ninguno y sin repetir. Si puedes ir a la derecha o hacia arriba, cambia el orden de los pasos. Cada orden distinto es un camino.",
                "Dos cuadras a la derecha y una hacia arriba.",
                "Los caminos son derecha-derecha-arriba, derecha-arriba-derecha y arriba-derecha-derecha. Hay 3.",
                [
                    C("Para ir de casa al parque das 2 cuadras a la derecha y 1 hacia arriba, en cualquier orden. ¿Cuántos caminos distintos hay?", ["2", "3", "4", "6"], "3", "Los tres órdenes son DDU, DUD y UDD.", "El paso hacia arriba puede ir primero, en el medio o al final."),
                    C("Una lámpara está encendida. Pulsas el interruptor 5 veces. ¿Cómo queda?", ["Encendida", "Apagada"], "Apagada", "Cada pulso cambia el estado. Un número impar de pulsos la deja al revés de como empezó.", "Cada vez que pulsas, la luz cambia. Prueba con 1 pulso y luego con 3."),
                    N("Empiezas en 0 y cada paso suma 2. Después de 4 pasos, ¿en qué número estás?", "8", "2 + 2 + 2 + 2 = 8. También 4 × 2 = 8.", "Son 4 saltos de 2. Puedes sumarlos o multiplicar."),
                    C("Tienes las llaves A y B, y el orden importa. ¿Cuántos órdenes distintos hay?", ["1", "2", "4", "8"], "2", "Puedes usar primero A y luego B, o primero B y luego A. Hay 2 órdenes.", "Escríbelas: primero A y después B, o primero B y después A."),
                ],
            ),
            _lesson(
                "edades",
                "Edades y cantidades",
                "Traduces las palabras ahora, antes y después a sumas o restas.",
                (6,),
                "«Ahora» es el número que te dan. «Dentro de unos años» se suma. «Hace unos años» se resta. «Tiene menos» también se resta.",
                "Camilo tiene 10 años. Su hermana tiene 3 años menos.",
                "10 − 3 = 7. La hermana tiene 7 años.",
                [
                    N("Camilo tiene 10 años. Su hermana tiene 3 menos. ¿Cuántos años tiene ella?", "7", "10 − 3 = 7.", "«Menos» quiere decir restar."),
                    N("Camilo tiene 10. ¿Cuántos años tendrá dentro de 4 años?", "14", "10 + 4 = 14.", "«Dentro de» quiere decir sumar esos años."),
                    N("Camilo tiene 10 y su hermana 7. ¿Cuánto suman sus edades hoy?", "17", "10 + 7 = 17.", "Suma las dos edades de hoy."),
                    N("La hermana tiene 7. ¿Cuántos años tenía hace 2 años?", "5", "7 − 2 = 5.", "«Hace» quiere decir restar esos años."),
                ],
            ),
            _lesson(
                "pensar-al-reves",
                "Pensar al revés",
                "Si conoces el final de la cuenta, deshaces las operaciones para hallar el inicio.",
                (6,),
                "Si sabes cómo terminó la cuenta, deshazla desde el final. Lo que se sumó, se quita. Lo que se multiplicó, se divide. Lo que se dividió, se multiplica.",
                "Pienso un número, le sumo 5 y obtengo 12.",
                "Al revés: 12 − 5 = 7. El número es 7.",
                [
                    N("Pienso un número, le sumo 5 y obtengo 12. ¿Cuál es?", "7", "12 − 5 = 7.", "Quita con una resta lo que se había sumado."),
                    N("Lo multiplico por 3 y obtengo 18. ¿Cuál es el número?", "6", "18 ÷ 3 = 6.", "Para deshacer una multiplicación, divide."),
                    N("Lo divido entre 2 y obtengo 9. ¿Cuál es el número?", "18", "9 × 2 = 18.", "Para deshacer una división, multiplica."),
                    N("Le resto 4 y después multiplico por 2. Obtengo 10. ¿Cuál es el número?", "9", "Primero deshaz el ×2: 10 ÷ 2 = 5. Ese 5 es el número menos 4. 5 + 4 = 9.", "Empieza por el final: primero deshaz la multiplicación y después la resta."),
                ],
            ),
        ),
    ),
)

MODULES = apply_figures(MODULES)
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


TRIAL: tuple[Problem, ...] = (
    Problem(
        id="prueba-suma",
        prompt="¿Cuánto es 6 + 5?",
        kind="choice",
        explain="6 + 5 = 11.",
        hint="",
        choices=(("11", "11"), ("10", "10"), ("12", "12")),
        answers=("11",),
    ),
    Problem(
        id="prueba-resta",
        prompt="¿Cuánto es 9 − 4?",
        kind="choice",
        explain="9 − 4 = 5.",
        hint="",
        choices=(("4", "4"), ("5", "5"), ("6", "6")),
        answers=("5",),
    ),
    Problem(
        id="prueba-producto",
        prompt="¿Cuánto es 3 × 4?",
        kind="choice",
        explain="3 × 4 = 12.",
        hint="",
        choices=(("7", "7"), ("12", "12"), ("34", "34")),
        answers=("12",),
    ),
)


def trial_problem(problem_id: str) -> Problem | None:
    for problem in TRIAL:
        if problem.id == problem_id:
            return problem
    return None


def public_problem(problem: Problem) -> dict:
    data = {
        "id": problem.id,
        "prompt": problem.prompt,
        "kind": problem.kind,
        "hint": problem.hint,
    }
    if problem.kind == "choice":
        data["choices"] = [{"id": choice_id, "label": label} for choice_id, label in problem.choices]
    if problem.scene:
        data["scene"] = problem.scene
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
