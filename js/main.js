/* Studio Saphy — lógica mínima.
   Dos páginas: index (grilla + filtro) y proyecto.html (?p=slug).
   Sin dependencias, sin fetch: los datos vienen de js/data.js. */
(function () {
	'use strict';

	var PROYECTOS = window.PROJECTS || [];
	var e = function (tag, cls) {
		var n = document.createElement(tag);
		if (cls) n.className = cls;
		return n;
	};

	function img(src, src640, w, h, alt, sizes, lazy) {
		var i = e('img');
		i.src = src;
		i.srcset = src640 + ' 640w, ' + src + ' ' + w + 'w';
		i.sizes = sizes;
		i.width = w;
		i.height = h;
		i.alt = alt;
		if (lazy) i.loading = 'lazy';
		return i;
	}

	/* ---------- index.html ---------- */

	function grilla() {
		var cont = document.getElementById('grilla');
		var filtros = document.getElementById('filtros');
		if (!cont || !filtros) return;

		var categorias = [];
		PROYECTOS.forEach(function (p) {
			if (categorias.indexOf(p.categoria) === -1) categorias.push(p.categoria);
		});

		function pintar(filtro) {
			cont.textContent = '';
			PROYECTOS.forEach(function (p) {
				if (filtro && p.categoria !== filtro) return;

				var a = e('a', 'proyecto');
				a.href = 'proyecto.html?p=' + encodeURIComponent(p.slug);

				var fig = e('figure');
				fig.appendChild(img(p.portada, p.portada640, p.portada_w, p.portada_h,
					p.nombre + ' — ' + p.categoria, '(max-width: 760px) 100vw, 45vw', true));

				var cap = e('figcaption');
				var nom = e('span', 'nombre');
				nom.textContent = p.nombre;
				var cat = e('span', 'categoria');
				cat.textContent = p.categoria;
				cap.appendChild(nom);
				cap.appendChild(cat);

				a.appendChild(fig);
				a.appendChild(cap);
				cont.appendChild(a);
			});
		}

		['Todo'].concat(categorias).forEach(function (cat) {
			var b = e('button');
			b.type = 'button';
			b.textContent = cat;
			b.setAttribute('aria-pressed', cat === 'Todo' ? 'true' : 'false');
			b.addEventListener('click', function () {
				Array.prototype.forEach.call(filtros.children, function (o) {
					o.setAttribute('aria-pressed', 'false');
				});
				b.setAttribute('aria-pressed', 'true');
				pintar(cat === 'Todo' ? null : cat);
			});
			filtros.appendChild(b);
		});

		pintar(null);
	}

	/* ---------- proyecto.html ---------- */

	function ficha() {
		var cont = document.getElementById('ficha');
		if (!cont) return;

		var slug = new URLSearchParams(window.location.search).get('p');
		var i = -1;
		PROYECTOS.forEach(function (p, k) { if (p.slug === slug) i = k; });

		if (i === -1) {
			var aviso = e('div', 'u-wrap ficha');
			var txt = e('div', 'ficha-txt');
			var h1f = e('h1');
			h1f.textContent = 'Proyecto no encontrado';
			var af = e('a');
			af.href = 'index.html#proyectos';
			af.textContent = 'Ver todos los proyectos';
			txt.appendChild(h1f);
			txt.appendChild(af);
			aviso.appendChild(txt);
			cont.appendChild(aviso);
			return;
		}

		var p = PROYECTOS[i];
		document.title = p.nombre + ' — Studio Saphy';

		var art = e('article');

		/* Cabecera: imagen + texto */
		var cab = e('div', 'u-wrap ficha');
		var fig = e('figure', 'ficha-img');
		fig.appendChild(img(p.portada, p.portada640, p.portada_w, p.portada_h,
			p.nombre + ' — ' + p.categoria, '(max-width: 760px) 90vw, 55vw', false));

		var txt = e('div', 'ficha-txt');
		var lab = e('span', 'u-label');
		lab.textContent = p.categoria;
		var h1 = e('h1');
		h1.textContent = p.nombre;
		txt.appendChild(lab);
		txt.appendChild(h1);
		if (p.descripcion) {
			var par = e('p');
			par.textContent = p.descripcion;
			txt.appendChild(par);
		}

		cab.appendChild(fig);
		cab.appendChild(txt);
		art.appendChild(cab);

		/* Galería. Se ordena para que las imágenes anchas abran la sección y las
		   demás queden en parejas: así la grilla de dos columnas no deja huecos. */
		var resto = p.imagenes.filter(function (im) { return im.src !== p.portada; });
		if (resto.length) {
			var piezas = resto.map(function (im) { return { im: im, ancha: im.w >= 1000 }; });
			var medias = piezas.filter(function (z) { return !z.ancha; });
			if (medias.length % 2 === 1) medias.pop().ancha = true;   // el sobrante ocupa la fila
			piezas = piezas.filter(function (z) { return z.ancha; })
				.concat(medias.sort(function (a, b) { return 0; }));

			var gal = e('div', 'u-wrap galeria');
			piezas.forEach(function (z, k) {
				var g = e('figure', z.ancha ? 'ancha' : '');
				g.appendChild(img(z.im.src, z.im.src640, z.im.w, z.im.h,
					p.nombre + ' — imagen ' + (k + 2),
					z.ancha ? '(max-width: 1440px) 90vw, 1200px' : '(max-width: 760px) 90vw, 45vw',
					true));
				gal.appendChild(g);
			});
			art.appendChild(gal);
		}

		/* Navegación anterior / siguiente */
		var nav = e('div', 'u-wrap paso');
		var prev = i > 0 ? PROYECTOS[i - 1] : null;
		var next = i < PROYECTOS.length - 1 ? PROYECTOS[i + 1] : null;

		var aPrev = e('a');
		aPrev.href = prev ? 'proyecto.html?p=' + encodeURIComponent(prev.slug) : 'index.html#proyectos';
		aPrev.textContent = prev ? '← ' + prev.nombre : '← Proyectos';

		var aNext = e('a');
		aNext.href = next ? 'proyecto.html?p=' + encodeURIComponent(next.slug) : 'index.html#proyectos';
		aNext.textContent = next ? next.nombre + ' →' : 'Proyectos →';

		nav.appendChild(aPrev);
		nav.appendChild(aNext);
		art.appendChild(nav);

		cont.appendChild(art);
	}

	grilla();
	ficha();
})();
