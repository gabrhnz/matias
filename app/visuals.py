"""Escenas de fracciones y geometría. El navegador las dibuja."""

from __future__ import annotations

from dataclasses import replace

VISUALS: dict[str, dict] = {
    "partes-de-un-entero-p1": {"prompt": "¿Qué fracción está pintada?", "scene": {"type": "pie", "parts": 4, "filled": 1}},
    "partes-de-un-entero-p2": {"prompt": "¿Qué fracción está pintada?", "scene": {"type": "pie", "parts": 8, "filled": 3}},
    "partes-de-un-entero-p3": {"prompt": "¿Qué número está señalado?", "scene": {"type": "notation", "num": 3, "den": 8, "mark": "den"}},
    "partes-de-un-entero-p4": {"prompt": "¿Qué fracción está pintada?", "scene": {"type": "bar", "parts": 6, "filled": 2}},
    "leer-fracciones-p1": {"prompt": "¿Cómo se lee?", "scene": {"type": "pie", "parts": 3, "filled": 2, "caption": "2/3"}},
    "leer-fracciones-p2": {"prompt": "¿Cómo se lee?", "scene": {"type": "pie", "parts": 2, "filled": 1, "caption": "1/2"}},
    "leer-fracciones-p3": {"prompt": "¿Cómo se lee?", "scene": {"type": "pie", "parts": 4, "filled": 3, "caption": "3/4"}},
    "leer-fracciones-p4": {"prompt": "¿Cómo se lee?", "scene": {"type": "pie", "parts": 8, "filled": 5, "caption": "5/8"}},
    "fracciones-equivalentes-p1": {"prompt": "¿Cuál pinta lo mismo?", "scene": {"type": "pie", "parts": 2, "filled": 1, "caption": "1/2"}},
    "fracciones-equivalentes-p2": {"prompt": "¿Cuál pinta lo mismo?", "scene": {"type": "pie", "parts": 3, "filled": 1, "caption": "1/3"}},
    "fracciones-equivalentes-p3": {
        "prompt": "¿Pintan la misma cantidad?",
        "scene": {"type": "pair", "items": [{"parts": 4, "filled": 2, "label": "2/4"}, {"parts": 2, "filled": 1, "label": "1/2"}]},
    },
    "fracciones-equivalentes-p4": {"prompt": "¿Cuál pinta lo mismo?", "scene": {"type": "pie", "parts": 6, "filled": 3, "caption": "3/6"}},
    "comparar-fracciones-p1": {
        "prompt": "¿Cuál es mayor?",
        "scene": {"type": "pair", "items": [{"parts": 2, "filled": 1, "label": "1/2"}, {"parts": 4, "filled": 1, "label": "1/4"}]},
    },
    "comparar-fracciones-p2": {
        "prompt": "¿Cuál es mayor?",
        "scene": {"type": "pair", "items": [{"parts": 3, "filled": 2, "label": "2/3"}, {"parts": 3, "filled": 1, "label": "1/3"}]},
    },
    "comparar-fracciones-p3": {
        "prompt": "¿Qué pasa con estas dos?",
        "scene": {"type": "pair", "items": [{"parts": 2, "filled": 1, "label": "1/2"}, {"parts": 4, "filled": 2, "label": "2/4"}]},
    },
    "comparar-fracciones-p4": {
        "prompt": "¿Cuál es mayor?",
        "scene": {"type": "pair", "items": [{"parts": 8, "filled": 3, "label": "3/8"}, {"parts": 8, "filled": 5, "label": "5/8"}]},
    },
    "sumar-fracciones-p1": {"prompt": "¿Cuánto es?", "scene": {"type": "sum", "parts": 5, "left": 1, "right": 2}},
    "sumar-fracciones-p2": {"prompt": "¿Cuánto es?", "scene": {"type": "sum", "parts": 8, "left": 2, "right": 3}},
    "sumar-fracciones-p3": {"prompt": "¿Cuánto es? Puedes simplificar.", "scene": {"type": "sum", "parts": 4, "left": 1, "right": 1}},
    "sumar-fracciones-p4": {"prompt": "¿Cuánto es?", "scene": {"type": "sum", "parts": 10, "left": 3, "right": 4, "shape": "bar"}},
    "restar-fracciones-p1": {"prompt": "¿Cuánto queda? Puedes simplificar.", "scene": {"type": "subtract", "parts": 6, "filled": 4, "remove": 1}},
    "restar-fracciones-p2": {"prompt": "¿Cuánto queda?", "scene": {"type": "subtract", "parts": 7, "filled": 5, "remove": 2}},
    "restar-fracciones-p3": {"prompt": "¿Cuánto queda? Puedes simplificar.", "scene": {"type": "subtract", "parts": 4, "filled": 3, "remove": 1}},
    "restar-fracciones-p4": {"prompt": "¿Cuánto queda del litro?", "scene": {"type": "subtract", "parts": 8, "filled": 7, "remove": 2}},
    "fraccion-de-una-cantidad-p1": {"prompt": "¿Cuántos son la mitad?", "scene": {"type": "share", "count": 10, "label": "1/2"}},
    "fraccion-de-una-cantidad-p2": {"prompt": "¿Cuántos son un cuarto?", "scene": {"type": "share", "count": 20, "label": "1/4"}},
    "fraccion-de-una-cantidad-p3": {"prompt": "¿Cuántos son dos tercios?", "scene": {"type": "share", "count": 9, "label": "2/3"}},
    "fraccion-de-una-cantidad-p4": {"prompt": "¿Cuántos son tres quintos?", "scene": {"type": "share", "count": 15, "label": "3/5"}},
    "numeros-mixtos-p1": {"prompt": "¿Cuántos enteros completos hay?", "scene": {"type": "improper", "parts": 4, "count": 7}},
    "numeros-mixtos-p2": {"prompt": "¿Qué fracción impropia es?", "scene": {"type": "mixed", "wholes": 1, "parts": 2, "filled": 1}},
    "numeros-mixtos-p3": {"prompt": "¿Cuántos tercios sobran?", "scene": {"type": "improper", "parts": 3, "count": 11}},
    "numeros-mixtos-p4": {"prompt": "¿Qué fracción impropia es?", "scene": {"type": "mixed", "wholes": 2, "parts": 4, "filled": 1}},
    "figuras-planas-p1": {"prompt": "¿Cómo se llama?", "scene": {"type": "shape", "shape": "triangle"}},
    "figuras-planas-p2": {"prompt": "¿Cómo se llama?", "scene": {"type": "shape", "shape": "square"}},
    "figuras-planas-p3": {"prompt": "¿Cómo se llama?", "scene": {"type": "shape", "shape": "circle"}},
    "figuras-planas-p4": {"prompt": "¿Cómo se llama?", "scene": {"type": "shape", "shape": "rectangle"}},
    "lados-y-vertices-p1": {"prompt": "¿Cuántos vértices tiene?", "scene": {"type": "shape", "shape": "triangle", "vertices": True}},
    "lados-y-vertices-p2": {"prompt": "¿Cuántos lados tiene?", "scene": {"type": "shape", "shape": "square"}},
    "lados-y-vertices-p3": {"prompt": "¿Cuántos lados tiene?", "scene": {"type": "shape", "shape": "pentagon"}},
    "lados-y-vertices-p4": {"prompt": "¿Cuántos vértices tiene?", "scene": {"type": "shape", "shape": "rectangle", "vertices": True}},
    "perimetro-p1": {"prompt": "¿Cuánto mide el borde?", "scene": {"type": "shape", "shape": "square", "w": 5, "h": 5}},
    "perimetro-p2": {"prompt": "¿Cuánto mide el borde?", "scene": {"type": "shape", "shape": "rectangle", "w": 6, "h": 3}},
    "perimetro-p3": {"prompt": "¿Cuánto mide el borde?", "scene": {"type": "shape", "shape": "triangle", "sides": [4, 4, 3]}},
    "perimetro-p4": {"prompt": "¿Cuántos metros de cerca?", "scene": {"type": "shape", "shape": "rectangle", "w": 8, "h": 2, "unit": "m"}},
    "area-del-rectangulo-p1": {"prompt": "¿Cuánta superficie cubre?", "scene": {"type": "shape", "shape": "rectangle", "w": 4, "h": 3, "filled": True}},
    "area-del-rectangulo-p2": {"prompt": "¿Cuánta superficie cubre?", "scene": {"type": "shape", "shape": "rectangle", "w": 7, "h": 2, "filled": True}},
    "area-del-rectangulo-p3": {"prompt": "¿Cuánta superficie cubre?", "scene": {"type": "shape", "shape": "square", "w": 6, "h": 6, "filled": True}},
    "area-del-rectangulo-p4": {"prompt": "¿Cuánta superficie cubre?", "scene": {"type": "shape", "shape": "rectangle", "w": 5, "h": 4, "unit": "m", "filled": True}},
    "area-del-triangulo-p1": {"prompt": "¿Cuál es el área?", "scene": {"type": "triangle-area", "base": 6, "height": 4}},
    "area-del-triangulo-p2": {"prompt": "¿Cuál es el área?", "scene": {"type": "triangle-area", "base": 10, "height": 3}},
    "area-del-triangulo-p3": {"prompt": "¿Cuál es el área?", "scene": {"type": "triangle-area", "base": 8, "height": 5}},
    "area-del-triangulo-p4": {"prompt": "¿Cuál es el área?", "scene": {"type": "triangle-area", "base": 7, "height": 2}},
    "simetria-p1": {"prompt": "¿Tiene eje de simetría?", "scene": {"type": "shape", "shape": "square"}},
    "simetria-p2": {"prompt": "¿Tiene un eje vertical?", "scene": {"type": "shape", "shape": "letter-a"}},
    "simetria-p3": {"prompt": "¿Cuántos ejes tiene?", "scene": {"type": "shape", "shape": "circle"}},
    "simetria-p4": {"prompt": "¿Cuántos ejes tiene?", "scene": {"type": "shape", "shape": "heart"}},
    "angulos-p1": {"prompt": "¿Cuánto mide?", "scene": {"type": "angle", "kind": "right"}},
    "angulos-p2": {"prompt": "¿Cómo se llama?", "scene": {"type": "angle", "kind": "acute"}},
    "angulos-p3": {"prompt": "¿Cómo se llama?", "scene": {"type": "angle", "kind": "obtuse"}},
    "angulos-p4": {"prompt": "¿Qué ángulo es la esquina?", "scene": {"type": "angle", "kind": "corner"}},
    "volumen-de-una-caja-p1": {"prompt": "¿Cuál es el volumen?", "scene": {"type": "prism", "w": 2, "h": 3, "d": 4}},
    "volumen-de-una-caja-p2": {"prompt": "¿Cuál es el volumen?", "scene": {"type": "prism", "w": 3, "h": 3, "d": 3}},
    "volumen-de-una-caja-p3": {"prompt": "¿Cuál es el volumen?", "scene": {"type": "prism", "w": 5, "h": 2, "d": 2}},
    "volumen-de-una-caja-p4": {"prompt": "¿Cuál es el volumen?", "scene": {"type": "prism", "w": 10, "h": 4, "d": 3}},
}

EXAMPLES: dict[str, dict] = {
    "partes-de-un-entero": {"type": "pie", "parts": 4, "filled": 1},
    "leer-fracciones": {"type": "pie", "parts": 4, "filled": 3, "caption": "3/4"},
    "fracciones-equivalentes": {"type": "pair", "items": [{"parts": 2, "filled": 1, "label": "1/2"}, {"parts": 4, "filled": 2, "label": "2/4"}]},
    "comparar-fracciones": {"type": "pair", "items": [{"parts": 2, "filled": 1, "label": "1/2"}, {"parts": 4, "filled": 1, "label": "1/4"}]},
    "sumar-fracciones": {"type": "sum", "parts": 5, "left": 1, "right": 2},
    "restar-fracciones": {"type": "subtract", "parts": 7, "filled": 5, "remove": 2},
    "fraccion-de-una-cantidad": {"type": "share", "count": 10, "label": "1/2"},
    "numeros-mixtos": {"type": "improper", "parts": 4, "count": 7},
    "figuras-planas": {"type": "shape", "shape": "triangle"},
    "lados-y-vertices": {"type": "shape", "shape": "triangle", "vertices": True},
    "perimetro": {"type": "shape", "shape": "square", "w": 5, "h": 5},
    "area-del-rectangulo": {"type": "shape", "shape": "rectangle", "w": 4, "h": 3, "filled": True},
    "area-del-triangulo": {"type": "triangle-area", "base": 6, "height": 4},
    "simetria": {"type": "shape", "shape": "letter-a"},
    "angulos": {"type": "angle", "kind": "right"},
    "volumen-de-una-caja": {"type": "prism", "w": 2, "h": 3, "d": 4},
}


def apply_figures(modules: tuple) -> tuple:
    updated = []
    for module in modules:
        if module.slug not in {"fracciones", "geometria"}:
            updated.append(module)
            continue
        lessons = []
        for lesson in module.lessons:
            problems = []
            for problem in lesson.problems:
                spec = VISUALS[problem.id]
                problems.append(replace(problem, prompt=spec["prompt"], scene=spec["scene"]))
            lessons.append(replace(lesson, problems=tuple(problems), example_scene=EXAMPLES.get(lesson.id)))
        updated.append(replace(module, lessons=tuple(lessons)))
    return tuple(updated)
