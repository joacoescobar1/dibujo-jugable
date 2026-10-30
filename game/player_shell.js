(function(){try{var h=document.head;if(!document.querySelector('meta[name=theme-color]')){h.insertAdjacentHTML('beforeend','<meta name="theme-color" content="#2a1f4a"><link rel="manifest" href="manifest.webmanifest"><meta name="apple-mobile-web-app-capable" content="yes">')}
var v=document.querySelector('meta[name=viewport]');if(!v){v=document.createElement('meta');v.name='viewport';h.appendChild(v);}var c=v.getAttribute('content')||'width=device-width,initial-scale=1';if(!/maximum-scale/.test(c))c+=(c.trim()?',' : '')+'maximum-scale=1,user-scalable=no';if(!/viewport-fit/.test(c))c+=',viewport-fit=cover';v.setAttribute('content',c);
var q0=new URLSearchParams(location.search);if(q0.get('judge')==='1'){document.documentElement.classList.add('lab');if(document.body)document.body.classList.add('lab');}else{document.documentElement.classList.add('playboot');var boot=document.createElement('style');boot.textContent='html.playboot,html.playboot body{margin:0;background:#07050f;overflow:hidden;height:100%;height:100svh;height:100dvh}html.playboot #side,html.playboot #hud,html.playboot #draw,html.playboot #rchips,html.playboot #beats,html.playboot #story,html.playboot #banner,html.playboot .sub,html.playboot>body>h1{display:none!important}html.playboot #gamecard,html.playboot .row,html.playboot #wrap{position:fixed!important;inset:0!important;width:100%!important;height:100%!important;height:100svh!important;height:100dvh!important;max-width:none!important;padding:0!important;margin:0!important;background:#07050f!important;border-radius:0!important;box-shadow:none!important}html.playboot #c,html.playboot #c3d{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;max-width:none!important;border-radius:0!important;box-shadow:none!important}';h.appendChild(boot);}}catch(e){}})();
// Player mode (default when the bundle has B.play, unless ?judge=1): fullscreen world.
// Gallery Play opens an honest saved-demo card. ?create=1 is a local photo + audio-only path and never claims an AI or Meta check.
(() => {
  const B = window.__BUNDLE__, q = new URLSearchParams(location.search);
  const ES = q.get('lang') === 'es', T = (en, es) => ES ? es : en;
  const DICT = {"Mariposa":"Butterfly","Sol":"Sun","Flor rosa":"Pink flower","Flor violeta":"Purple flower","Flor amarilla":"Yellow flower","Nube gris":"Gray cloud","Nube gris monstruo":"Gray cloud monster","Nene del medio":"Kid in the middle","Nene en el subibaja":"Kid on the seesaw","Nene de la izquierda":"Kid on the left","Nena en el tobogan":"Kid on the slide","Nena de la derecha":"Kid on the right","Puerta brillante":"Glowing door","Puerta a las nubes":"Door to the clouds","Puerta brillante del festejo":"Glowing party door","¡Listo, campeón! Ahora la mariposa tiene que juntar a los tres nenes para ganar y el sol queda brillando de decorado en el cielo.":"All set, champ! Now the butterfly has to collect the three kids to win, and the sun stays shining as decoration in the sky.","Brasa vuela con los dragones amigos al castillo":"Brasa flies with the dragon friends to the castle","Brasa, el dragón, empieza a volar al castillo":"Brasa the dragon starts flying to the castle","Brasa, el dragón, llega al castillo":"Brasa the dragon reaches the castle","El camino de piedras de Rocco":"Rocco's rocky path","El cielo":"The sky","El cielo con nubes grises":"The sky with gray clouds","El círculo y el agua azul":"The circle and the blue water","El despegue de Nova":"Nova's takeoff","El fantasma camina por abajo":"The ghost walks underneath","El fantasma que camina por abajo":"The ghost that walks underneath","El festejo del gato":"The cat's celebration","El festejo del hueso":"The bone celebration","El gato aprende a esquivar el agua":"The cat learns to dodge the water","El gato quiere el hueso pero hay fuego":"The cat wants the bone but there is fire","El gato tiene que llegar a la casa, no puede tocar el agua":"The cat has to reach the house and can't touch the water","El gato va a la casa sin tocar el agua y hay un fantasma que camina por abajo":"The cat goes to the house without touching the water, and a ghost walks underneath","El gato y su primer hueso":"The cat and his first bone","El monstruo cuida el camino":"The monster guards the path","El monstruo cuida la estrella":"The monster guards the star","El monstruo cuida las estrellas":"The monster guards the stars","El muro de piedras y el planeta rosa":"The stone wall and the pink planet","El patio":"The playground","El patio del perro":"The dog's yard","El perro busca el hueso y no puede tocar el fuego":"The dog looks for the bone and can't touch the fire","El perro tiene que llegar a la estrella sin tocar las piedras":"The dog has to reach the star without touching the rocks","El perro va a la casa y hay agua en el medio":"The dog goes to the house and there is water in the middle","El perro y el agua en el medio":"The dog and the water in the middle","El pico de fuego":"The peak of fire","El primer hueso":"The first bone","El río azul y los 3 gatos amigos":"The blue river and the 3 cat friends","El sol":"The sun","El vuelo valiente de Tizón":"Tizón's brave flight","Gato -> Hueso":"Cat → Bone","La banda roja de fuego":"The red band of fire","La casa del perro":"The dog's house","La estrella final":"The final star","La estrella final de Rocco":"Rocco's final star","La estrella guardada por el monstruo":"The star guarded by the monster","La estrellita final de Milo":"Milo's final little star","La franja roja de fuego":"The red stripe of fire","La llegada a la estrella":"Arriving at the star","La mariposa lleva a los tres nenes al sol":"The butterfly carries the three kids to the sun","La mariposa tiene que llevar a los tres nenes en su lomo a volar. No puede irse sin juntarlos a todos. Gana cuando los tres vuelan con ella hasta el sol.":"The butterfly has to carry the three kids on her back and fly. She can't leave without collecting all of them. She wins when all three fly with her to the sun.","La nave aprende a volar":"The ship learns to fly","La nave busca la casa":"The ship looks for the house","La nave busca la estrella esquivando las piedras pero un monstruo la cuida":"The ship looks for the star, dodging the rocks, but a monster guards it","La nave despega":"The ship takes off","La nave despega entre piedras":"The ship takes off among rocks","La nave despega hacia el sol":"The ship takes off toward the sun","La nave despega hacia la estrella":"The ship takes off toward the star","La nave esquiva las piedras":"The ship dodges the rocks","La nave llega a la estrella":"The ship reaches the star","La nave llega a la estrella esquivando las piedras":"The ship reaches the star by dodging the rocks","La voz dice que la mariposa junta a los 3 nenes antes de volar, pero win_condition=reach_goal y solo 0 nenes son goals: la mariposa puede irse sola. Hacé que los 3 nenes sean goals (ids nene_*) con win_condition collect_all; el sol queda como decorado (characters role=friend no se usa para nenes).":"The voice says the butterfly collects the 3 kids before flying, but win_condition=reach_goal and only 0 kids are goals: the butterfly can leave alone. Make the 3 kids goals (ids nene_*) with win_condition collect_all; the sun stays as decoration (characters role=friend is not used for the kids).","Mi nave tiene que llegar a la estrella sin tocar las piedras, pero hay un monstruo que la cuida":"My ship has to reach the star without touching the rocks, but a monster guards it","Milo aprende a correr":"Milo learns to run","Milo busca el hueso":"Milo looks for the bone","Milo empieza el camino":"Milo starts the path","Milo está chocho y orgulloso. «¡Plin, yo festejo bailando con mi huesito!»":"Milo is thrilled and proud. “Pling, I'm celebrating by dancing with my little bone!”","Milo está re feliz. «¡Fiuuu, yo voy por mi huesito!»":"Milo is so happy. “Wheee, I'm going for my little bone!”","Milo está valiente y gracioso. «¡Plop, yo junto los tres huesitos!»":"Milo is brave and funny. “Plop, I'm collecting the three little bones!”","Milo junta 3 estrellitas":"Milo collects 3 little stars","Milo llega a la casa":"Milo reaches the house","Milo y los fuegos que van y vienen":"Milo and the fires that come and go","Más agua en el medio":"More water in the middle","Nave -> Estrella":"Ship → Star","Nova busca entre las casas":"Nova searches among the houses","Nova llega feliz a la estrella final. ¡Yupi, a festejar!":"Nova arrives happy at the final star. Yay, let's celebrate!","Nova llega orgullosa y festeja con risas. ¡Wiii!":"Nova arrives proud and celebrates with laughs. Whee!","Nova ríe feliz entre piedritas bailarinas. ¡Plop!":"Nova laughs happily among dancing little rocks. Plop!","Nova saluda alegre al monstruito gracioso y sigue. ¡Plop!":"Nova waves happily at the funny little monster and goes on. Plop!","Perro -> Estrella":"Dog → Star","Perro -> Hueso":"Dog → Bone","Rocco busca la estrella":"Rocco looks for the star","Rocco está chocho y baila: «Yo llego a mi estrella». ¡Fiuuu, a festejar!":"Rocco is thrilled and dances: “I'm reaching my star.” Wheee, let's celebrate!","Rocco mueve la cola, re feliz: «Yo voy por mi estrella». ¡Fiuuu!":"Rocco wags his tail, so happy: “I'm going for my star.” Wheee!","Rocco salta entre piedras, re contento: «Yo esquivo y junto todo». ¡Plop, plop!":"Rocco jumps among rocks, so glad: “I dodge and collect everything.” Plop, plop!","Rocco y el camino de las piedras":"Rocco and the rocky path","Roco está chocho, moviendo la cola sin parar. ¡Guau! ¡Yo ya olí mi hueso riquísimo!":"Roco is thrilled, wagging his tail nonstop. Woof! I already smell my yummy bone!","Roco está re contento: ¡llegó el gran final! ¡Plop! ¡A festejar moviendo la cola!":"Roco is so happy: the big finale is here! Plop! Celebrate by wagging your tail!","Roco mira la franja roja y sonríe valiente. ¡Fiuuu! ¡Qué calorcito hace acá!":"Roco looks at the red stripe and smiles bravely. Wheee! It's toasty here!","Soy Nova, despego re feliz buscando mi estrella. ¡Fiuuu!":"I'm Nova, taking off so happy, looking for my star. Wheee!","Tizón llega al castillo":"Tizón reaches the castle","Tizón y el primer círculo":"Tizón and the first circle","Un dragon vuela al castillo":"A dragon flies to the castle","Yo soy Nova y despego feliz por mi estrella. ¡Fiuuu!":"I'm Nova and I take off happy for my star. Wheee!","el gatito corre a la estrellita":"the kitten runs to the little star","¡A volar entre nubes con los 3 nenes en el lomo!":"Fly among the clouds with the 3 kids on your back!","¡Bip bip! Astro está orgullosa y re feliz. «¡Yo llegué, a festejar!»":"Beep beep! Astro is proud and so happy. “I made it, let's celebrate!”","¡Buuu, jaja! Milo está curioso y re valiente hoy. Un fantasmita simpático camina y saluda por abajo.":"Boo, haha! Milo is curious and very brave today. A friendly little ghost walks and waves underneath.","¡El hueso final!":"The final bone!","¡Esquivando piedras!":"Dodging rocks!","¡Fiuuu! Astro está feliz, con cosquillitas en la panza. «¡Yo vuelo hoy!»":"Wheee! Astro is happy, with tummy tickles. “I fly today!”","¡Fiuuu! Milo está alegre y concentrado. ¡Yo busco amigos sin chapotear!":"Wheee! Milo is cheerful and focused. I'm looking for friends without splashing!","¡Fiuuu! Soy Milo y corro feliz a mi estrellita.":"Wheee! I'm Milo and I run happily to my little star.","¡Fiuuu! Soy Milo y quiero ese hueso, ¡qué alegría!":"Wheee! I'm Milo and I want that bone, what a joy!","¡Fiuuu! Soy Nova y busco mi estrella brillosa. ¡Dale, despegamos con alegría!":"Wheee! I'm Nova and I'm looking for my shiny star. Come on, we take off with joy!","¡Fiuuu! Soy Nova, re contenta, y busco mi casa.":"Wheee! I'm Nova, so glad, and I'm looking for my house.","¡Fiuuu! Soy Pipo y estoy valiente y contento. ¡Yo cruzo saltando por el hueco grande!":"Wheee! I'm Pipo and I'm brave and glad. I cross by jumping through the big gap!","¡Fiuuu! Yo soy Milo, re feliz. ¡Veo el círculo brillando!":"Wheee! I'm Milo, so happy. I see the circle shining!","¡Fiuuu! Yo soy Nova, la nave re contenta. Rumbo al Sol, con una sonrisa enorme.":"Wheee! I'm Nova, the very happy ship. Heading for the Sun, with a huge smile.","¡Fiuuu! Yo soy Tizón. ¡Vuelo feliz y chocho al castillo!":"Wheee! I'm Tizón. I fly happy and thrilled to the castle!","¡Fiuuu! Yo, Brasa, despego re feliz rumbo al castillo.":"Wheee! I, Brasa, take off so happy toward the castle.","¡Fiuuu! Yo, Milo, estoy re contento: ¡salgo hacia mi casa! Patitas secas, pancita valiente y mucha ilusión.":"Wheee! I, Milo, am so glad: I'm heading to my house! Dry paws, a brave tummy, and lots of hope.","¡Fiuuu! Yo, Rocco, ya huelo mi estrella. ¡Vamos con alegría!":"Wheee! I, Rocco, can already smell my star. Let's go with joy!","¡Fiuuu, soy Nova y vuelo re contenta! ¡Vamos por esa Estrella brillante!":"Wheee, I'm Nova and I fly so glad! Let's go for that bright Star!","¡Guau! Soy Pipo y estoy re contento. ¡Yo olfateo mi hueso, qué rico!":"Woof! I'm Pipo and I'm so glad. I sniff my bone, yum!","¡Guau, Pipo mueve la colita re feliz! ¡Yo quiero llegar a mi casita!":"Woof, Pipo wags his little tail so happy! I want to reach my little house!","¡Guauuu! Milo, llegó el hueso grande, ¡a festejar con alegría!":"Wooof! Milo, the big bone is here, let's celebrate with joy!","¡Guauuu! ¡Bravo, Tizón! ¡Festejo con torta, bailecito y aplausos!":"Wooof! Bravo, Tizón! I celebrate with cake, a little dance, and applause!","¡Juntá a los 3 nenes en tu lomo!":"Collect the 3 kids on your back!","¡La casa de Milo!":"Milo's house!","¡La casa del gato!":"The cat's house!","¡Llegamos a la estrella!":"We reached the star!","¡Llegamos al sol!":"We reached the sun!","¡Miauuu! Milo está chochísimo: ¡ya llegó a su casa! ¡Festejo con saltitos, ronroneo y patitas secas!":"Meeoow! Milo is over the moon: he reached his house! I celebrate with little jumps, purrs, and dry paws!","¡Miauuu! Milo está contento y curioso. ¡Yo cruzo sin mojarme las patitas!":"Meeoow! Milo is glad and curious. I cross without getting my paws wet!","¡Milo y el hueso grande!":"Milo and the big bone!","¡Nova encuentra su casa!":"Nova finds her house!","¡Pipo mira las olitas traviesas y sonríe! ¡Plop, plop, a zigzaguear con alegría!":"Pipo looks at the naughty little waves and smiles! Plop, plop, zigzag with joy!","¡Pipo ya ve su casita y salta feliz! ¡Fiuuu, bailecito y gran festejo!":"Pipo can see his little house and jumps happily! Wheee, a little dance and a big celebration!","¡Plin! Yo soy Nova, re emocionada ante la Estrella. Después, bailecito espacial y muchos aplausos.":"Pling! I'm Nova, so excited before the Star. Then a little space dance and lots of applause.","¡Plin, plin! Bubu pasa por abajo. Milo ríe, re contento.":"Pling, pling! Bubu passes underneath. Milo laughs, so glad.","¡Plop! Astro está valiente y sonriente. «¡Yo paso saludando a Morado!»":"Plop! Astro is brave and smiling. “I go by waving at Morado!”","¡Plop! Grufo saluda a Nova con una sonrisa. ¡Zigzagueá de puntitas, campeona, vos podés!":"Plop! Grufo waves at Nova with a smile. Zigzag on tiptoes, champ, you can do it!","¡Plop! Milo está chocho y orgulloso. ¡Yo llegué, festejemos en casa!":"Plop! Milo is thrilled and proud. I made it, let's celebrate at home!","¡Plop! Milo salta contento entre tres estrellitas brillantes.":"Plop! Milo jumps gladly among three shiny little stars.","¡Plop! Milo, esos fueguitos bailan re graciosos, ¡qué emoción!":"Plop! Milo, those little fires dance so funny, how exciting!","¡Plop! Nova mira tres casas, re curiosa. ¡Qué lío lindo, che!":"Plop! Nova looks at three houses, so curious. What a lovely mess!","¡Plop! Rocco salta contento entre piedras. ¡Tres estrellas te esperan, campeón!":"Plop! Rocco jumps gladly among rocks. Three stars are waiting, champ!","¡Plop! Soy Pipo y estoy re feliz. ¡Yo festejo bailando con mi hueso!":"Plop! I'm Pipo and I'm so happy. I celebrate by dancing with my bone!","¡Plop! Yo soy Nova, re divertida ante el murallón. Del otro lado brilla el Planeta Rosa.":"Plop! I'm Nova, having so much fun before the big wall. On the other side the Pink Planet shines.","¡Plop! ¡Qué alegría, Brasa! ¡Tus amigos ya vienen volando!":"Plop! What a joy, Brasa! Your friends are already flying over!","¡Plop! ¡Qué risa, Tizón! Los cuadraditos bailan y dejan pasar.":"Plop! What a laugh, Tizón! The little squares dance and let you through.","¡Plop, qué risa, Nova, las piedras están bailando! Pasá tranqui cuando giren y reíte.":"Plop, what a laugh, Nova, the rocks are dancing! Go through calmly when they spin, and laugh.","¡Rocco llega a la estrella!":"Rocco reaches the star!","¡Taráaaan! Nova ve la estrella final, qué orgullo. ¡Juntála, Nova: baile y aplausos!":"Ta-daaa! Nova sees the final star, what pride. Collect it, Nova: dance and applause!","¡Wiii! Milo llega orgulloso y festejamos juntos.":"Whee! Milo arrives proud and we celebrate together.","¡Wiiiii, qué alegría enorme, Nova! ¡Festejá fuerte junto a la Estrella Final!":"Wheeee, what huge joy, Nova! Celebrate loud next to the Final Star!","¡Yupi! Nova encontró su casa, re feliz. ¡Fiesta, confeti y abrazos!":"Yay! Nova found her house, so happy. Party, confetti, and hugs!","¡Yupi! Rocco mueve la cola, re feliz. ¡A festejar bailando, genio!":"Yay! Rocco wags his tail, so happy. Let's celebrate by dancing, genius!","¡Yupii! Milo llegó a su casa, re feliz. ¡A festejar!":"Yay! Milo reached his house, so happy. Let's celebrate!","¡Yupiii! ¡Bravo, Brasa! ¡Fiesta y aplausos en el castillo!":"Yay! Bravo, Brasa! Party and applause at the castle!","¡Último vuelo tranquilo hasta el sol!":"One last calm flight to the sun!"};
  const FB = [[/estrellitas/gi, 'little stars'], [/estrellita/gi, 'little star'], [/estrellas/gi, 'stars'], [/estrella/gi, 'star'], [/nenes/gi, 'kids'], [/nena/gi, 'girl'], [/nene/gi, 'kid'], [/fantasmita/gi, 'little ghost'], [/fantasma/gi, 'ghost'], [/monstruito/gi, 'little monster'], [/monstruo/gi, 'monster'], [/piedritas/gi, 'little rocks'], [/piedras/gi, 'rocks'], [/piedra/gi, 'rock'], [/huesitos/gi, 'little bones'], [/huesito/gi, 'little bone'], [/huesos/gi, 'bones'], [/hueso/gi, 'bone'], [/castillo/gi, 'castle'], [/casita/gi, 'little house'], [/casas/gi, 'houses'], [/casa/gi, 'house'], [/agua/gi, 'water'], [/fueguitos/gi, 'little fires'], [/fuegos/gi, 'fires'], [/fuego/gi, 'fire'], [/nubes/gi, 'clouds'], [/nube/gi, 'cloud'], [/mariposa/gi, 'butterfly'], [/gatito/gi, 'kitten'], [/gatos/gi, 'cats'], [/gato/gi, 'cat'], [/perrito/gi, 'puppy'], [/perro/gi, 'dog'], [/nave/gi, 'ship'], [/dragones/gi, 'dragons'], [/drag[oó]n|dragon/gi, 'dragon'], [/escenas/gi, 'scenes'], [/escena/gi, 'scene'], [/juntalos|juntá|junta/gi, 'collect'], [/esquivá|esquiva/gi, 'dodge'], [/llegá|llega/gi, 'reach'], [/puerta/gi, 'door']];
  const PHRASE = [[/el dibujo original/gi, "the original drawing"], [/del dibujo/gi, "of the drawing"], [/arranca trabado/gi, "starts out stuck"], [/no puede tocar/gi, "can't touch"], [/sin tocar/gi, "without touching"], [/tiene que/gi, "has to"], [/por abajo/gi, "underneath"], [/por arriba/gi, "over the top"], [/va a la/gi, "goes to the"], [/va al/gi, "goes to the"], [/vuela al/gi, "flies to the"], [/llega a la/gi, "reaches the"], [/llega al/gi, "reaches the"], [/busca la/gi, "looks for the"], [/busca el/gi, "looks for the"], [/hay una/gi, "there is a"], [/hay un/gi, "there is a"], [/no puede/gi, "can't"], [/\bllegar\b/gi, "reach"], [/\bvolar\b/gi, "fly"], [/\bentre\b/gi, "between"]];
  const GLUE = [[/\bpero\b/gi, "but"], [/\bcon\b/gi, "with"], [/\bsin\b/gi, "without"], [/\bpara\b/gi, "for"], [/\bporque\b/gi, "because"], [/\bdel\b/gi, "of the"], [/\bal\b/gi, "to the"], [/\bde la\b/gi, "of the"], [/\bde los\b/gi, "of the"], [/\bde las\b/gi, "of the"], [/\bpor\b/gi, "by"], [/\blos\b/gi, "the"], [/\blas\b/gi, "the"], [/\bel\b/gi, "the"], [/\bla\b/gi, "the"], [/\buna\b/gi, "a"], [/\bun\b/gi, "a"], [/\bque\b/gi, "that"], [/\by\b/gi, "and"], [/\bhay\b/gi, "there is"], [/\bpuede\b/gi, "can"], [/\bquiere\b/gi, "wants"], [/\bbusca\b/gi, "looks for"], [/\bvuela\b/gi, "flies"], [/\bllega\b/gi, "reaches"], [/\btiene\b/gi, "has"], [/\barranca\b/gi, "starts"], [/\btrabado\b/gi, "stuck"], [/\btocar\b/gi, "touch"]];
  const LEAK = /[áéíóúñÁÉÍÓÚÑ¿¡]|\b(el|la|los|las|una|del|hay|tiene|quiere|busca|puede|tocar|vuela|volar|llega|llegar|entre|escena|puerta|nene|nena|mariposa|gato|perro|nave|hueso|estrella|castillo|fuego|agua|piedra|fantasma|monstruo|dibujo|juego|jugar|junt\w*|pasos|trabado|arranca|abajo|arriba|por)\b/i;
  const ACC = { á: "a", é: "e", í: "i", ó: "o", ú: "u", ñ: "n", Á: "A", É: "E", Í: "I", Ó: "O", Ú: "U", Ñ: "N" };
  const tr = s => {
    if (s == null) return "";
    s = String(s);
    if (ES || !s) return s;
    if (Object.prototype.hasOwnProperty.call(DICT, s)) return DICT[s];
    let o = s;
    for (const [re, en] of PHRASE) o = o.replace(re, en);
    for (const [re, en] of FB) o = o.replace(re, en);
    if (!LEAK.test(o)) return o;
    for (const [re, en] of GLUE) o = o.replace(re, en);
    o = o.replace(/[áéíóúñÁÉÍÓÚÑ¿¡]/g, ch => ACC[ch] || "");
    o = o.replace(/\s+/g, " ").replace(/\s+([,.!?;:])/g, "$1").trim();
    if (o && /[a-z]/i.test(o[0]) && o[0] === o[0].toLowerCase()) o = o[0].toUpperCase() + o.slice(1);
    return o;
  };
  window.__tr = tr;
  const RUN_KEY = 'dj_run_v1';
  function loadRun() { try { const r = JSON.parse(sessionStorage.getItem(RUN_KEY) || 'null'); return r && typeof r === 'object' ? r : null; } catch (e) { return null; } }
  function saveRun(r) { window.__RUN__ = r; try { sessionStorage.setItem(RUN_KEY, JSON.stringify(r)); } catch (e) {} }
  function freshRun() { const r = { t0: Date.now(), stars: 0, got: {}, sample: (B && B.sample) || '' }; saveRun(r); return r; }
  function ensureRun() {
    const sample = (B && B.sample) || '', level = (B && B.play && B.play.level) || 1;
    if (level === 1 && q.get('go') !== '1') return freshRun();
    const r = loadRun();
    if (!r || r.sample !== sample || !r.t0) return freshRun();
    saveRun(r); return r;
  }
  // Optional playground bonus. Not a goal, wall, or door, so the solver path stays the same.
  (function placeSpark() {
    const sample = (B && B.sample) || '', level = (B && B.play && B.play.level) || 1;
    const on = /playground_01/.test(sample) && level === 1;
    const run = ensureRun();
    window.__SPARK__ = { cell: on ? { x: 4, y: 3, id: 'spark_patio' } : null, got: false, score: run.stars || 0 };
  })();
  function englishChrome() {
    const reps = [
      [/el dibujo original/g, "the original drawing"],
      [/del dibujo/g, "of the drawing"],
      [/arranca trabado/gi, "starts out stuck"],
      [/Dibujo Jugable — demo para jueces/g, "Playable Drawing — judge demo"],
      [/Un nene dibuja \+ cuenta su juego → el agente genera, juega, falla, arregla, hasta poder ganarlo\./g, "A kid draws and tells their game. The agent builds it, plays it, fails, fixes it, until it can be won."],
      [/▶ Modo juez \(recorrido automático\)/g, "▶ Judge tour (auto playthrough)"],
      [/1\. Dibujo del nene → Meta lo procesa/g, "1. The kid's drawing, turned into a game"],
      [/1\. Dibujo → render pro \(Meta\)/g, "1. Drawing → game render"],
      [/Transcripción de voz/g, "Voice transcript"],
      [/2\. Loop del agente \(episode\.jsonl\)/g, "2. Agent loop"],
      [/click = ver ese intento/g, "click = view that attempt"],
      [/3\. Juego \(jugable: flechas · R reinicia\)/g, "3. Game (arrows to move · R restarts)"],
      [/— intento /g, "— attempt "],
      [/Intento agente:/g, "Agent attempt:"],
      [/Intento #/g, "Attempt #"],
      [/Intento:/g, "Attempt:"],
      [/ de (\d+):/g, " of $1:"],
      [/✅ ganable en /g, "✅ winnable in "],
      [/ · ganable en /g, " · winnable in "],
      [/(\d+) pasos/g, "$1 steps"],
      [/el agente lo jugó en Chromium contra el juego real/g, "the agent played it in Chromium against the real game"],
      [/Tocá /g, "Tap "],
      [/▶ Ver al agente jugar \(solver\)/g, "▶ Watch the agent play (solver)"],
      [/▶ Ver al agente intentarlo \(y fallar\)/g, "▶ Watch the agent try (and fail)"],
      [/▶ Ver al agente jugar/g, "▶ Watch the agent play"],
      [/el agente lo jugó y NO se puede ganar/g, "the agent played it and it CANNOT be won"],
      [/Arreglo mínimo que aplica/g, "Smallest fix applied"],
      [/GANABLE/g, "WINNABLE"],
      [/🖍️ Dibujo \+ voz/g, "🖍️ Drawing + voice"],
      [/regla de voz: la mariposa se fue sin juntar a los 3 nenes/g, "voice rule: the butterfly left without collecting the 3 kids"],
      [/regla de voz: la mariposa se fue sin los 3 nenes/g, "voice rule: the butterfly left without the 3 kids"],
      [/un enemigo tapa todos los caminos a la meta/g, "an enemy blocks every path to the goal"],
      [/no hay camino a la meta sin tocar peligros\/paredes\/enemigos/g, "no path to the goal without touching hazards, walls, or enemies"],
      [/el jugador nace adentro de un peligro/g, "the player spawns inside a hazard"],
      [/el jugador nace encima de un enemigo/g, "the player spawns on an enemy"],
      [/no se puede sobrevivir: lo acorralan/g, "cannot survive: the player is cornered"],
      [/Flechas para mover · R reinicia/g, "Arrows to move · R restarts"],
      [/R para reiniciar/g, "R to restart"],
      [/Pasos:/g, "Steps:"],
      [/Estado:/g, "Status:"],
      [/Timeline del agente/g, "Agent timeline"],
      [/🎨 Jugar demos · Para jueces →/g, "🎨 Play demos · For judges →"],
      [/Dibujo Jugable/g, "Playable Drawing"],
      [/✏️ dibujo original/g, "✏️ original drawing"],
      [/⚙️ Meta procesando…/g, "⚙️ Building the game…"],
      [/✨ render Meta \(pasá el mouse: original\)/g, "✨ game render (hover: original)"],
      [/🔍 SAM recorta/g, "🔍 cut out"],
      [/🎨 Image ilumina/g, "🎨 light it"],
      [/🎮 render jugable/g, "🎮 playable render"],
      [/Evidencia QA \(screenshot headless\)/g, "QA evidence (headless screenshot)"],
      [/Screenshot headless \(Chromium contra game\.js\):/g, "Headless screenshot (Chromium against game.js):"],
      [/screenshot embebido \(no necesita runs\/\)/g, "embedded screenshot (no runs/ folder)"],
      [/\(sin --browser\)/g, "(no --browser)"],
      [/\(el agente prueba la ruta más corta y choca justo con el bug 🐞 → por eso hace falta el arreglo\)/g, "(the agent tries the shortest route and hits the bug, so a fix is needed)"],
      [/→ arreglo en 3 s…/g, "→ fix in 3 s…"],
      [/llamadas Meta=/g, "Meta calls="],
      [/en vivo/g, "live"],
      [/SIN SALIDA/g, "NO WAY OUT"],
      [/TRABADO/g, "STUCK"],
      [/¡GANASTE!/g, "YOU WIN!"],
      [/¡TE ATRAPÓ!/g, "CAUGHT!"],
      [/PERDISTE/g, "YOU LOSE"],
      [/¡Te fuiste sin los 3 nenes!/g, "You left without the 3 kids!"],
      [/\bjugando\b/g, "playing"],
      [/\bGANÓ\b/g, "WON"],
      [/\bPERDIÓ\b/g, "LOST"],
      [/le cambió el ritmo al (.+?) para que deje pasar/g, "changed $1's rhythm so you can pass"],
      [/corrió al (.+?) un poquito: ya no tapa el camino/g, "nudged $1 so the path is open"],
      [/movió al jugador \((.+?)\)/g, "moved the player ($1)"],
      [/abrió un puente sobre /g, "opened a bridge over "],
      [/abrió una puerta en la pared que encerraba la meta/g, "opened a door in the wall that trapped the goal"],
      [/no encontró un arreglo mínimo/g, "no small fix found"]
    ];
    const looksEs = s => /[áéíóúñÁÉÍÓÚÑ¿¡]|\b(junt\w*|escenas?|puertas?|nenes|nene|nena|mariposas?|jugando|ganable|ganaste|intentos?|dibujos?|dibuja|jugar|juego|tocá|deslizá|pasos|reiniciar|arreglo|estrellas?|huesos?|castillo|flechas|jurado|juez|galería|sonido|pausa|arriba|abajo|izquierda|derecha|subibaja|tobogan|nubes?|flores?|brillante|campeón|transcripción|jugable|procesando|agente|llamadas|estado|evidencia|contra|sin|salida|trabado|ilumina|recorta|ganó|perdió|perdiste|arranca|patitas|pancita|el|la|los|las|hay|tiene|quiere|busca|puede|tocar|vuela|llegar)\b/i.test(s);
    const keys = Object.keys(DICT).filter(k => k.length > 15).sort((a, b) => b.length - a.length);
    const localize = v => {
      let o = String(v);
      if (!looksEs(o)) return o;
      for (const [re, en] of reps) o = o.replace(re, en);
      const trim = o.trim();
      if (trim && Object.prototype.hasOwnProperty.call(DICT, trim)) return o.replace(trim, tr(trim));
      const quoted = trim.match(/^[“"]([\s\S]+)[”"]$/);
      if (quoted && Object.prototype.hasOwnProperty.call(DICT, quoted[1])) return o.replace(quoted[1], tr(quoted[1]));
      for (const k of keys) if (o.includes(k)) { o = o.replace(k, DICT[k]); break; }
      if (looksEs(o)) o = tr(o);
      return o;
    };
    const mapNode = node => {
      if (!node) return;
      if (node.nodeType === 3) {
        const p = node.parentElement;
        if (!p || p.tagName === "SCRIPT" || p.tagName === "STYLE") return;
        const n2 = localize(node.nodeValue);
        if (n2 !== node.nodeValue) node.nodeValue = n2;
        return;
      }
      if (node.nodeType !== 1 || node.tagName === "SCRIPT" || node.tagName === "STYLE") return;
      for (const attr of ["alt", "title", "aria-label", "placeholder"]) {
        if (!node.hasAttribute || !node.hasAttribute(attr)) continue;
        const v = node.getAttribute(attr);
        const n2 = localize(v);
        if (n2 !== v) node.setAttribute(attr, n2);
      }
      for (const ch of [...node.childNodes]) mapNode(ch);
    };
    const run = () => { if (run.lock) return; run.lock = true; try { mapNode(document.body); if (document.title) { const t2 = localize(document.title); if (t2 !== document.title) document.title = t2; } document.documentElement.lang = "en"; } finally { run.lock = false; } };
    run();
    try { new MutationObserver(() => run()).observe(document.documentElement, { subtree: true, childList: true, characterData: true }); } catch (e) {}
  }
  if (!ES) englishChrome();
  if (q.get('judge') === '1') { document.documentElement.classList.add('lab'); document.body.classList.add('lab'); }
  if (!B || !B.play || q.get('judge') === '1') { document.documentElement.classList.remove('playboot'); return; }
  const P = B.play, last = !P.next, drawing = B.photo_src || (B.drawing_b64 ? 'data:image/png;base64,' + B.drawing_b64 : ''), hero = B.title_b64 ? 'data:image/png;base64,' + B.title_b64 : drawing;
  document.documentElement.classList.add('play');
  document.body.classList.add('play');
  document.body.classList.remove('lab');
  document.documentElement.classList.remove('lab');
  document.documentElement.classList.remove('playboot');
  const css = document.createElement('style'); css.textContent = `
html.play,body.play{margin:0;overflow:hidden;background:#07050f;touch-action:none;-webkit-text-size-adjust:100%;-webkit-user-select:none;user-select:none;height:100%;height:100svh;height:100dvh;min-height:100svh;min-height:100dvh}
body.play>*:not(.row):not(#mu):not(#ps):not(#wipe):not(#hud3):not(#jt):not(#pz):not(#pzo):not(#skip):not(#tale):not(#dpad):not(#stick):not(#onb):not(#home):not(#demoNote):not(#gate):not(#combo):not(script):not(style){display:none!important}
body.play #side,body.play #hud,body.play #draw,body.play #rchips,body.play #beats,body.play #story,body.play #banner,body.play .sub,body.play>h1,body.play #gamecard>*:not(#wrap){display:none!important}
body.play .row{display:block!important;margin:0;position:fixed;inset:0;width:100%;height:100%;height:100svh;height:100dvh}body.play #gamecard{font-size:0;color:transparent;position:fixed;inset:0;width:100%;height:100%;height:100svh;height:100dvh;padding:0!important;margin:0;background:#07050f;border-radius:0;display:block;box-shadow:none}
body.play #wrap{position:fixed!important;inset:0!important;width:100%!important;width:100vw!important;height:100%!important;height:100svh!important;height:100dvh!important;max-width:none!important;padding:0!important;background:none!important;box-shadow:none!important;border-radius:0!important}body.play #wrap::after{display:none}
body.play #c,body.play #c3d{position:absolute!important;left:0!important;top:0!important;width:100%!important;height:100%!important;max-width:none!important;max-height:none!important;border-radius:0!important;box-shadow:none!important}body.play #c3d{border-radius:0!important;box-shadow:none!important}body.s3d.play #c{opacity:0!important}
body.play #c,body.play #c3d,body.play #wrap,body.play #gamecard{touch-action:none}
body.play #ps{position:relative!important;z-index:70!important}
#ps .scr{position:fixed;inset:0;z-index:88;background:radial-gradient(120% 90% at 50% 20%,#2a1f4aee,#07050ff5 70%);display:flex;flex-direction:column;align-items:center;justify-content:center;justify-content:safe center;gap:18px;color:#fff;font-family:"Comic Sans MS","Chalkboard SE",cursive;text-align:center;transition:opacity .35s;overflow:auto;padding:calc(88px + env(safe-area-inset-top)) 12px calc(16px + env(safe-area-inset-bottom));touch-action:pan-y;-webkit-overflow-scrolling:touch}
#ps .scr.off{opacity:0;pointer-events:none}
#ps .bg{position:absolute;inset:0;background-size:cover;background-position:center;filter:blur(6px) brightness(.45) saturate(1.3);transform:scale(1.08);z-index:-1;animation:kb 18s ease-in-out infinite alternate}
@keyframes kb{to{transform:scale(1.2) translate(-2%,-2%)}}
#ps h1{font-size:clamp(42px,8vw,110px);margin:0;background:linear-gradient(180deg,#fff6c2,#ffb347 60%,#ff6fa5);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 6px 0 #0008) drop-shadow(0 0 30px #ffb34788);animation:bob 2.4s ease-in-out infinite}
@keyframes bob{50%{transform:translateY(-8px) rotate(-1deg)}}
#ps .big{font:800 clamp(22px,3vw,34px) inherit;padding:18px 54px;border:0;border-radius:999px;cursor:pointer;color:#2b1600;background:linear-gradient(180deg,#ffe27a,#ff9f1c);box-shadow:0 8px 0 #b35c00,0 18px 40px #ff9f1c66;transition:transform .12s;min-height:64px}
#ps .big:hover{transform:translateY(-3px) scale(1.04)}#ps .big:active{transform:translateY(5px);box-shadow:0 3px 0 #b35c00}
#ps .ghost{background:#ffffff14;color:#fff;box-shadow:0 0 0 2px #ffffff44 inset;font-size:18px;padding:12px 28px}
#ps .drop{display:flex;gap:18px}#ps .drop label{width:220px;height:170px;border-radius:22px;border:3px dashed #ffffff66;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;cursor:pointer;background:#ffffff0c;font-size:18px;overflow:hidden}
#ps .drop label img{max-width:100%;max-height:120px;border-radius:10px}#ps .drop input{display:none}
#ps .stage{position:relative;width:min(70vw,620px);aspect-ratio:4/3;border-radius:24px;overflow:hidden;box-shadow:0 30px 80px #000,0 0 0 4px #ffd27a55}
#ps .stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:filter 1s,opacity 1s}
#ps .robot{position:absolute;font-size:64px;left:-10%;bottom:12%;filter:drop-shadow(0 8px 6px #0008);transition:left 1.6s cubic-bezier(.5,0,.5,1),transform .2s}
#ps .beam{position:absolute;inset:0;background:linear-gradient(90deg,transparent,#6fe3ff55,transparent);transform:translateX(-100%);animation:scan 1.6s linear infinite}
@keyframes scan{to{transform:translateX(100%)}}
#ps .msg{font-size:clamp(22px,3vw,38px);font-weight:800;min-height:1.4em;text-shadow:0 4px 0 #0008}
#ps .bar{width:min(60vw,520px);height:14px;border-radius:9px;background:#ffffff1a;overflow:hidden}#ps .bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#6fe3ff,#b388ff,#ffd27a);transition:width .6s}
#ps .oops{animation:oops .5s}@keyframes oops{20%{transform:translateX(-14px) rotate(-2deg)}40%{transform:translateX(12px) rotate(2deg)}60%{transform:translateX(-8px)}}
#ps .stamp{position:absolute;inset:auto 0 18% 0;font-size:54px;font-weight:900;color:#7dffb0;text-shadow:0 0 30px #35e07a,0 5px 0 #0009;transform:scale(0) rotate(-12deg);transition:transform .45s cubic-bezier(.2,1.8,.4,1)}#ps .stamp.on{transform:scale(1) rotate(-6deg)}
#wipe{position:fixed;inset:0;z-index:96;pointer-events:none;background:#12081c;clip-path:circle(0% at 50% 50%);transition:clip-path .5s cubic-bezier(.7,0,.3,1);display:flex;align-items:center;justify-content:center;color:#ffd27a;font:900 clamp(30px,5vw,64px) "Comic Sans MS",cursive;text-shadow:0 4px 0 #3a2200}
#wipe.iris{clip-path:circle(0% at 50% 50%)}#wipe.iris.on{clip-path:circle(150% at 50% 50%)}
#wipe.band{clip-path:inset(0 0 0 100%);background:linear-gradient(100deg,#3a2468 0%,#12081c 46%,#07050f 100%)}#wipe.band.on{clip-path:inset(0 0 0 0)}
#wipe.on{clip-path:circle(150% at 50% 50%)}
body.transitioning #wipe{pointer-events:auto}
#combo{position:fixed;left:50%;top:28%;z-index:80;pointer-events:none;font:900 clamp(40px,12vw,78px) "Comic Sans MS",cursive;color:#fff6c2;text-shadow:0 4px 0 #b35c00,0 0 22px #ffd27a,-2px 0 #ff8ac2;opacity:0;transform:translate(-50%,-20%) scale(.2);white-space:nowrap;background:#2a1248f2;border:4px solid #ffd27a;border-radius:28px;padding:2px 22px 8px;box-shadow:0 8px 0 #0008}
#combo small{display:block;font-size:.42em;letter-spacing:.12em;text-transform:uppercase;color:#fff}
#combo.on{opacity:1;animation:comboPop .72s cubic-bezier(.2,1.5,.3,1) both}
@keyframes comboPop{0%{opacity:1;transform:translate(-50%,-8%) scale(.15) rotate(-8deg)}46%{opacity:1;transform:translate(-50%,-58%) scale(1.16) rotate(3deg)}100%{opacity:1;transform:translate(-50%,-72%) scale(1) rotate(0)}}
#hud3 #h3c span{background:none;padding:0;box-shadow:none;backdrop-filter:none;border-radius:0}#h3c .kicker{flex:0 0 auto;font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#ffd27a;font-weight:800;margin-right:6px}#h3c .obj{flex:1 1 auto;color:#fffaf2;font-weight:800;text-shadow:0 1px 0 #000,0 2px 10px #000c}#h3c .pips{display:inline-flex;gap:1px;align-items:center}#h3c .pip{font-size:30px;line-height:1;display:inline-block;transform-origin:50% 60%;filter:grayscale(1) brightness(1.6) opacity(.38)}#h3c .pip.on{filter:drop-shadow(0 0 6px #ffd27a);transform:scale(1.12)}#h3c .pip.pop{animation:pipop .5s cubic-bezier(.2,1.7,.3,1)}@keyframes pipop{0%{transform:scale(.15) rotate(-18deg)}42%{transform:scale(1.9) rotate(12deg)}70%{transform:scale(1) rotate(-6deg)}100%{transform:scale(1.12) rotate(0)}}#h3c.door .obj{color:#e7ffe9}#h3c.in{animation:banIn .32s cubic-bezier(.16,1,.3,1) both}#h3c.out{animation:banOut .18s ease forwards}@keyframes banIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}@keyframes banOut{to{opacity:0;transform:translateY(-8px)}}
#pzo .hint{font-size:20px;font-weight:600;opacity:.8;margin-top:-6px}#pzo .row2{display:flex;gap:14px}#pzo .sm{font-size:20px!important;padding:12px 28px!important;background:#ffffff22!important;color:#fff!important;box-shadow:none!important}
#ps .steps{display:flex;gap:10px;margin-top:-4px}#ps .steps b{min-width:120px;padding:8px 14px;border-radius:999px;background:#ffffff12;box-shadow:0 0 0 2px #ffffff22 inset;font-size:19px;font-weight:800;color:#ffffffaa;transition:.3s}#ps .steps b.now{background:#6fe3ff33;box-shadow:0 0 0 2px #6fe3ff inset;color:#fff;transform:scale(1.08)}#ps .steps b.bad{background:#ff8a8033;box-shadow:0 0 0 2px #ff8a80 inset;color:#fff}#ps .steps b.fix{background:#ffd27a33;box-shadow:0 0 0 2px #ffd27a inset;color:#fff}#ps .steps b.ok{background:#9effa833;box-shadow:0 0 0 2px #9effa8 inset;color:#fff;transform:scale(1.1)}
#hud3{position:fixed;top:calc(66px + env(safe-area-inset-top));left:calc(8px + env(safe-area-inset-left));right:calc(8px + env(safe-area-inset-right));z-index:40;display:flex;flex-direction:row;flex-wrap:wrap;align-items:center;gap:4px;font:800 16px "Comic Sans MS",cursive;color:#fff;pointer-events:none;max-width:100%}
#hud3 .pill{background:#120818cc;backdrop-filter:blur(8px);padding:4px 10px;font-size:13px;line-height:1.2;border-radius:999px;box-shadow:0 0 0 1px #ffd27a99;letter-spacing:0}
#h3c{color:#fffaf2;letter-spacing:.01em;background:#120818cc;padding:5px 10px 6px;font:800 clamp(13px,3.4vw,16px)/1.2 system-ui,"Segoe UI","Helvetica Neue",sans-serif;border-radius:12px;border-left:4px solid #ffd27a;box-shadow:0 4px 14px #0006,0 0 0 1px #ffffff22;display:flex;flex-wrap:wrap;align-items:center;column-gap:6px;row-gap:0;max-width:min(96vw,520px);flex:1 1 auto;min-width:0;text-wrap:balance}#pz,#mu{position:fixed;top:calc(8px + env(safe-area-inset-top));z-index:42;width:56px;height:56px;min-width:56px;min-height:56px;border-radius:50%;border:0;font-size:24px;background:#120818cc;color:#fff;cursor:pointer;box-shadow:0 0 0 2px #ffd27a99;touch-action:manipulation;backdrop-filter:blur(8px)}#pz{right:calc(8px + env(safe-area-inset-right))}#mu{right:calc(72px + env(safe-area-inset-right))!important;top:calc(8px + env(safe-area-inset-top))!important}#pzo{position:fixed;inset:0;z-index:95;background:#07050fcc;backdrop-filter:blur(8px);display:none;flex-direction:column;align-items:center;justify-content:center;gap:16px;color:#fff;font:900 clamp(36px,9vw,56px) 'Comic Sans MS',cursive;padding:calc(16px + env(safe-area-inset-top)) 14px calc(16px + env(safe-area-inset-bottom));text-align:center}#pzo.on{display:flex}#pzo button{font:800 clamp(18px,4.5vw,28px) 'Comic Sans MS',cursive;padding:16px 28px;min-height:64px;border:0;border-radius:999px;background:linear-gradient(180deg,#ffe27a,#ff9f1c);box-shadow:0 8px 0 #b35c00;cursor:pointer}#skip{position:fixed;right:calc(16px + env(safe-area-inset-right));bottom:calc(16px + env(safe-area-inset-bottom));z-index:70;font:800 20px 'Comic Sans MS',cursive;padding:14px 22px;min-height:56px;border:0;border-radius:999px;background:#ffffff22;color:#fff;cursor:pointer;box-shadow:0 0 0 2px #ffffff55 inset}#tale{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom));z-index:45;max-width:min(88vw,640px);background:#120818f6;color:#fffaf2;padding:14px 22px 16px;border-radius:18px;border-left:5px solid #ffd27a;font:800 clamp(20px,4.8vw,32px)/1.28 system-ui,"Segoe UI","Helvetica Neue",sans-serif;text-align:center;box-shadow:0 18px 50px #000c,0 0 0 1px #ffffff22;opacity:0;transform:translateX(-50%) translateY(16px);transition:opacity .28s ease,transform .32s cubic-bezier(.16,1,.3,1)}#tale.in{opacity:1;transform:translateX(-50%) translateY(0)}#tale.out{opacity:0;transform:translateX(-50%) translateY(12px)}#tale .kicker{display:block;font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#ffd27a;margin-bottom:4px}#tale .hint{font-size:14px;font-weight:650;opacity:.75;margin-top:8px}#jt{position:fixed;right:calc(12px + env(safe-area-inset-right));top:calc(90px + env(safe-area-inset-top));bottom:auto;z-index:41;color:#ffffff55;font:12px sans-serif;text-decoration:none;padding:8px}
#ps .duo{display:flex;gap:22px;align-items:center}#ps .duo img{width:min(36vw,440px);border-radius:20px;box-shadow:0 20px 60px #000}#ps .duo b{font-size:60px}
body.play #ov{background:none!important}body.play #ov #ovt,body.play #ov small{opacity:0}
#dpad{position:fixed;z-index:46;left:auto;right:calc(10px + env(safe-area-inset-right));bottom:calc(10px + env(safe-area-inset-bottom));width:248px;height:248px;display:grid;grid-template-columns:76px 76px 76px;grid-template-rows:76px 76px 76px;gap:10px;touch-action:none;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;background:none}
#dpad[hidden]{display:none!important}#dpad button{width:76px;height:76px;min-width:64px;min-height:64px;border-radius:50%;border:0;padding:0;font-size:34px;line-height:1;display:flex;align-items:center;justify-content:center;background:#0006;color:#fff;box-shadow:0 0 0 2px #ffd27aaa,0 8px 18px #0005;touch-action:none;cursor:pointer;pointer-events:auto;backdrop-filter:blur(4px)}#dpad button:active{transform:translateY(2px);box-shadow:0 0 0 3px #fff,0 4px 10px #0005}#dpad .u{grid-column:2;grid-row:1}#dpad .l{grid-column:1;grid-row:2}#dpad .r{grid-column:3;grid-row:2}#dpad .d{grid-column:2;grid-row:3}
#stick{position:fixed;z-index:45;left:calc(14px + env(safe-area-inset-left));bottom:calc(14px + env(safe-area-inset-bottom));width:156px;height:156px;border-radius:50%;touch-action:none;pointer-events:none;-webkit-user-select:none;user-select:none;background:none}
#stick[hidden]{display:none!important}#stick.float{bottom:auto}
#stick .ring{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle,#ffffff18 0 46%,#00000033 62%,#00000044 78%);box-shadow:0 0 0 3px #ffd27a88,inset 0 0 18px #6fe3ff44}
#stick .ring::after{content:"";position:absolute;left:50%;top:50%;width:28%;height:28%;transform:translate(-50%,-50%);border-radius:50%;border:2px dashed #ffffff88}
#stick .knob{position:absolute;left:50%;top:50%;width:68px;height:68px;min-width:64px;min-height:64px;margin:-34px 0 0 -34px;border-radius:50%;background:radial-gradient(circle at 38% 32%,#fff,#ffe27a 42%,#ff9f1c);box-shadow:0 8px 0 #b35c0099,0 0 0 3px #fff8}
#stick.hot .ring{box-shadow:0 0 0 5px #fff,inset 0 0 22px #6fe3ff88}
@media (max-width:700px){#dpad{width:208px;height:208px;grid-template-columns:64px 64px 64px;grid-template-rows:64px 64px 64px;gap:8px}#dpad button{width:64px;height:64px;min-width:64px;min-height:64px;font-size:28px}#stick{width:140px;height:140px}#stick .knob{width:64px;height:64px;margin:-32px 0 0 -32px}}
#onb{position:fixed;inset:0;z-index:94;background:#07050fe0;display:flex;align-items:center;justify-content:center;padding:calc(18px + env(safe-area-inset-top)) 16px calc(18px + env(safe-area-inset-bottom));touch-action:none}#onb .card{width:min(92vw,520px);background:#241545;color:#fff;border-radius:28px;padding:26px 18px;box-shadow:0 0 0 4px #ffd27a,0 24px 60px #000;display:flex;flex-direction:column;gap:14px;font:800 clamp(22px,6vw,34px)/1.35 "Comic Sans MS","Chalkboard SE",cursive;text-align:center}#onb .go{font-size:clamp(16px,4vw,20px);opacity:.75}
body.touch #skip{bottom:calc(268px + env(safe-area-inset-bottom))}
#pzo .hint{max-width:min(92vw,520px)}#pzo .row2{flex-wrap:wrap;justify-content:center}
@media (max-width:430px){#ps .drop{flex-direction:column;gap:10px}#ps .drop label{width:min(86vw,300px);height:112px}#ps .duo{flex-direction:column;gap:8px}#ps .duo img{width:min(78vw,320px)}#ps .duo b{font-size:36px}#ps .stage{width:min(92vw,620px)}#ps .steps{flex-wrap:wrap;justify-content:center;max-width:94vw}#ps .steps b{min-width:0}}
#finale{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;align-items:center;min-height:36px;font-size:34px;pointer-events:none}
#finale i{font-style:normal;display:inline-block;opacity:0;transform:scale(.2)}
#finale i.on{opacity:1;animation:finPop .5s cubic-bezier(.2,1.7,.3,1) both}
#finale.still i,#finale.still .yay{opacity:1;transform:none;animation:none!important}
#finale .yay{opacity:0;font:900 clamp(16px,4vw,22px) "Comic Sans MS",cursive;color:#fff6c2;text-shadow:0 3px 0 #0008}
#finale .yay.on{opacity:1}
@keyframes finPop{0%{opacity:1;transform:scale(.15) rotate(-16deg)}55%{transform:scale(1.28) rotate(8deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
@media (prefers-reduced-motion:reduce){#h3c.in,#h3c.out,#h3c .pip.pop,#combo.on,#tale .art,#finale,#finale i,#ps h1,#ps .bg{animation:none!important}#tale{transition:none!important}#combo.on{opacity:1;transform:translate(-50%,-50%) scale(1)}#finale i,#finale .yay{opacity:1;transform:none}#wipe,#wipe.iris,#wipe.band{transition-duration:.01ms!important}}
#home{position:fixed;z-index:71;top:calc(8px + env(safe-area-inset-top));left:calc(8px + env(safe-area-inset-left));min-height:56px;height:56px;min-width:96px;padding:0 12px;display:flex;align-items:center;justify-content:center;border-radius:16px;background:#120818cc;color:#fffaf2;text-decoration:none;font:800 16px/1 "Comic Sans MS","Chalkboard SE",cursive;box-shadow:0 0 0 2px #ffd27aaa,0 6px 14px #0006;touch-action:manipulation;backdrop-filter:blur(8px)}
#pzo a.home{min-height:64px;min-width:180px;padding:16px 28px;border-radius:999px;background:#ffffff22;color:#fff;text-decoration:none;font:800 clamp(18px,4.5vw,28px)/1 "Comic Sans MS",cursive;box-shadow:0 0 0 2px #ffffff55 inset;display:inline-flex;align-items:center;justify-content:center;touch-action:manipulation}
body.play #gate.on{position:fixed!important;inset:0!important;z-index:80!important;display:flex!important;pointer-events:auto!important;border-radius:0!important}
body.modal-open #dpad,body.modal-open #stick,body.transitioning #dpad,body.transitioning #stick{display:none!important;pointer-events:none!important}
#demoNote{position:fixed;inset:0;z-index:93;background:#07050ee8;display:flex;align-items:center;justify-content:center;padding:calc(18px + env(safe-area-inset-top)) 16px calc(18px + env(safe-area-inset-bottom));touch-action:none}
#demoNote .card{width:min(92vw,520px);background:#241545;color:#fff;border-radius:28px;padding:22px 18px;box-shadow:0 0 0 4px #ffd27a,0 24px 60px #000;display:flex;flex-direction:column;gap:12px;align-items:center;font:800 clamp(18px,4.6vw,26px)/1.35 "Comic Sans MS","Chalkboard SE",cursive;text-align:center}
#demoNote img{width:min(70vw,280px);max-height:220px;object-fit:contain;border-radius:16px;background:#0006}
#demoNote .tr{font-size:clamp(14px,3.6vw,18px);font-weight:650;opacity:.9}
#demoNote .big{font:800 clamp(20px,5vw,28px) inherit;padding:16px 36px;min-height:64px;border:0;border-radius:999px;cursor:pointer;color:#2b1600;background:linear-gradient(180deg,#ffe27a,#ff9f1c);box-shadow:0 8px 0 #b35c00}
#hud3{top:calc(66px + env(safe-area-inset-top));left:calc(8px + env(safe-area-inset-left));right:calc(8px + env(safe-area-inset-right));gap:4px}
#hud3 .pill{background:#120818cc;color:#fffaf2;padding:4px 10px;min-height:28px;font:800 14px/1.15 "Comic Sans MS","Chalkboard SE",cursive;border-radius:999px;box-shadow:0 0 0 2px #ffd27a99;letter-spacing:.01em;display:inline-flex;align-items:center}
#h3c{max-width:min(96vw,520px)}#h3c .kicker{font-size:9px;letter-spacing:.12em}
#h3c .obj{font-size:clamp(13px,3.4vw,16px)}#h3c .pip{font-size:18px}
#pz{background:#ffd27acc;color:#2b1600;box-shadow:0 0 0 2px #fff8;font-size:24px}
#mu{box-shadow:0 0 0 2px #ffd27a99}
#pzo #jt{position:static;top:auto;right:auto;bottom:auto;z-index:1;min-height:56px;min-width:180px;padding:14px 22px;border-radius:999px;background:#ffffff22;color:#fff;text-decoration:none;font:800 20px/1 "Comic Sans MS","Chalkboard SE",cursive;box-shadow:0 0 0 2px #ffffff55 inset;display:inline-flex;align-items:center;justify-content:center;touch-action:manipulation}
#onb .kicker{font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:#ffd27a}
#tale{position:fixed;inset:0;left:0;top:0;right:0;bottom:0;z-index:92;width:auto;height:auto;max-width:none;margin:0;display:flex;align-items:center;justify-content:center;padding:calc(18px + env(safe-area-inset-top)) calc(16px + env(safe-area-inset-right)) calc(18px + env(safe-area-inset-bottom)) calc(16px + env(safe-area-inset-left));background:#07050ee8;color:#fffaf2;border:0;border-radius:0;box-shadow:none;opacity:1;transform:none;transition:none;touch-action:none;cursor:pointer;font:800 clamp(22px,5.4vw,34px)/1.3 "Comic Sans MS","Chalkboard SE",cursive;text-align:center}
body.touch #tale{left:0;bottom:0;transform:none}
#tale .card{width:min(92vw,520px);background:#241545;border-radius:28px;padding:22px 18px 18px;box-shadow:0 0 0 4px #ffd27a,0 24px 60px #000;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none}
#tale .kicker{display:block;font-size:14px;letter-spacing:.16em;text-transform:uppercase;color:#ffd27a;margin:0}
#tale .art{font-size:96px;line-height:1;margin:2px 0}
#tale .line{margin:0;font:800 clamp(22px,5.4vw,34px)/1.3 "Comic Sans MS","Chalkboard SE",cursive;color:#fffaf2}
#tale .hint{font:700 18px/1.3 system-ui,"Segoe UI",sans-serif;color:#ffd27a;margin-top:6px}
@media (prefers-reduced-motion:no-preference){#tale .art{animation:taleBob 1.8s ease-in-out infinite}}
@keyframes taleBob{50%{transform:translateY(-8px) scale(1.05)}}
#h3spark{min-height:44px}#h3spark[hidden]{display:none!important}
#sparkpop{display:none;align-self:flex-start;background:#2a1248f2;color:#fff6c2;border:3px solid #ffd27a;border-radius:16px;padding:6px 12px;font:900 22px "Comic Sans MS",cursive;box-shadow:0 6px 0 #0008}
#sparkpop.on{display:inline-flex}
#results{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;max-width:min(96vw,640px)}
#results b{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:8px 14px;border-radius:16px;background:#120818f5;box-shadow:0 0 0 3px #ffd27a;font-size:clamp(16px,4.2vw,22px);color:#fffaf2}
#onb,#demoNote,#tale,#pzo{overflow:auto}
@media (max-height:520px){
#ps .scr{justify-content:flex-start;gap:8px;padding-top:calc(64px + env(safe-area-inset-top))}
#ps h1{font-size:28px}
#ps .duo img{max-height:72px;width:auto;max-width:min(40vw,200px);object-fit:contain}
#ps .scr .msg{font-size:16px!important}
#ps .big{min-height:56px;padding:10px 18px;font-size:18px}
#hud3{top:calc(68px + env(safe-area-inset-top))!important}
#hud3 .pill{min-height:32px;font-size:16px;padding:4px 10px}
#h3c{font-size:15px;padding:6px 10px;max-width:min(96vw,520px)}
#h3c .pip{font-size:18px}
#home{min-height:56px;height:56px;min-width:96px;font-size:18px;padding:0 10px}
#pz,#mu{width:56px;height:56px;min-width:56px;min-height:56px;font-size:26px}
#mu{right:calc(74px + env(safe-area-inset-right))!important}
#dpad{width:188px;height:188px;grid-template-columns:56px 56px 56px;grid-template-rows:56px 56px 56px;gap:10px;bottom:calc(6px + env(safe-area-inset-bottom));right:calc(6px + env(safe-area-inset-right))}
#dpad button{width:56px;height:56px;min-width:56px;min-height:56px;font-size:22px}
#stick{width:120px;height:120px}
#stick .knob{width:56px;height:56px;min-width:56px;min-height:56px;margin:-28px 0 0 -28px}
#tale .art{font-size:48px}
#onb .card,#demoNote .card,#tale .card{font-size:18px;padding:12px;gap:6px;margin:8px auto}
#demoNote img{max-height:72px}
#combo{top:16%;font-size:32px}
}
@media (prefers-reduced-motion:reduce){#tale,#tale .art,#sparkpop.on,#finale,#finale i,#ps h1,#ps .bg{animation:none!important;transition:none!important;transform:none!important}#finale i,#finale .yay{opacity:1}}
@media (max-height:430px) and (min-width:680px){
#ps .scr{overflow:hidden;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-content:center;justify-items:center;gap:2px 10px;padding:4px 10px 6px}
#ps .scr>h1,#ps .scr>.msg,#ps .scr>#results,#ps .scr>#finale,#ps .scr>.duo{grid-column:1 / -1}
#ps h1{font-size:22px;line-height:1.05;animation:none;margin:0}
#ps .scr .msg{font-size:14px!important;line-height:1.15;min-height:0}
#ps .duo{gap:8px}
#ps .duo img{max-height:56px;width:auto;max-width:160px;object-fit:cover}
#ps .duo b{font-size:22px}
#ps .big{min-height:56px;padding:6px 14px;font-size:16px;margin-top:0!important}
#results{gap:4px}
#results b{min-height:36px;font-size:15px;padding:2px 10px}
#finale{min-height:22px;font-size:20px;gap:4px}
#finale .yay{font-size:15px}
#ps .bg{transform:none!important;animation:none!important}
#hud3{top:6px!important;left:128px!important;right:138px!important;flex-direction:row;flex-wrap:nowrap;align-items:center;gap:6px;max-height:56px}
#hud3 .pill{min-height:36px;height:36px;font-size:15px;padding:4px 10px}
#h3spark{min-height:36px}
#h3c{flex:1 1 auto;min-width:0;max-width:none;max-height:48px;font-size:14px;padding:4px 10px;flex-wrap:nowrap;overflow:hidden}
#h3c .kicker{flex:0 0 auto;font-size:10px}
#h3c .obj{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
#h3c .pips{flex:0 0 auto}
#h3c .pip{font-size:16px}
#home{top:6px;height:56px;min-height:56px}
#pz,#mu{top:6px;width:56px;height:56px;min-width:56px;min-height:56px}
#mu{right:70px!important}
#pz{right:8px}
#dpad{width:188px;height:188px;grid-template-columns:56px 56px 56px;grid-template-rows:56px 56px 56px;gap:10px;bottom:6px;right:6px}
#dpad button{width:56px;height:56px;min-width:56px;min-height:56px}
#stick{width:112px;height:112px}
#stick .knob{width:56px;height:56px;min-width:56px;min-height:56px;margin:-28px 0 0 -28px}
#onb,#demoNote,#tale,#pzo{overflow:hidden}
#pzo{gap:6px;padding:8px 12px;font-size:22px;justify-content:center}
#pzo .title{font-size:22px;line-height:1.1}
#pzo .hint{font-size:14px;line-height:1.25;margin:0;max-width:680px}#pzo .row2{flex-wrap:nowrap;gap:8px}
#pzo button,#pzo a.home,#pzo #jt{min-height:56px;padding:8px 14px}
#onb .card,#demoNote .card{width:min(92vw,680px);font-size:16px;gap:6px;padding:10px 14px}
#onb .kicker{font-size:12px}
#demoNote img{max-height:56px;width:auto}
#demoNote .tr{font-size:14px;line-height:1.25}
#demoNote .big{min-height:56px;padding:8px 18px;font-size:18px}
#tale .card{width:min(94vw,760px);flex-direction:row;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 12px;padding:10px 14px;text-align:left}
#tale .kicker,#tale .hint{flex:1 0 100%;text-align:center;margin:0}
#tale .art{font-size:52px;margin:0}
#tale .line{flex:1 1 280px;font-size:18px;text-align:left;margin:0}
}`;
  document.head.appendChild(css);
  const ps = document.createElement('div'); ps.id = 'ps'; document.body.appendChild(ps);
  const el = (h) => { const d = document.createElement('div'); d.innerHTML = h.trim(); return d.firstChild; }, sl = ms => new Promise(r => setTimeout(r, ms));
  const REDUCED_MOTION = (() => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } })();
  const esc = s => String(s == null ? '' : s).replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch]));
  document.documentElement.lang = ES ? 'es' : 'en'; try { document.title = T('Playable Drawing', 'Dibujo Jugable'); } catch (e) {}
  const addQ = href => { const [p, s] = String(href).split('?'); const u = new URLSearchParams(s || ''); if (ES) u.set('lang', 'es'); if (q.get('mute')) u.set('mute', '1'); const qs = u.toString(); return (p || '') + (qs ? '?' + qs : ''); };
  const wipe = el('<div id="wipe"></div>'); document.body.appendChild(wipe);
  window.__JUICE__ = window.__JUICE__ || { dust: 0, combo: 0, transition: '', confetti: 0, shapes: [] };
  function fxLock(mode) {
    document.body.classList.add('transitioning');
    wipe.classList.remove('iris', 'band'); wipe.classList.add(mode === 'wipe' ? 'band' : 'iris');
    wipe.dataset.fx = mode === 'wipe' ? 'wipe' : 'iris';
    window.__JUICE__.transition = wipe.dataset.fx;
    const d = document.getElementById('dpad'), s = document.getElementById('stick');
    if (d) { d.hidden = true; d.setAttribute('aria-disabled', 'true'); d.querySelectorAll('button').forEach(b => { b.disabled = true; }); }
    if (s) s.hidden = true;
    try { syncModal(); } catch (e) {}
  }
  function revealPad() {
    const d = document.getElementById('dpad'), s = document.getElementById('stick');
    let open = false; try { open = overlayOpen(); } catch (e) {}
    if (!open && document.body.classList.contains('touch')) {
      if (d) { d.hidden = false; d.removeAttribute('aria-disabled'); d.querySelectorAll('button').forEach(b => { b.disabled = false; }); }
      if (s) s.hidden = false;
    }
    try { syncModal(); } catch (e) {}
  }
  function fxUnlock() {
    document.body.classList.remove('transitioning');
    window.__JUICE__.transition = '';
    revealPad();
  }
  const hud = el('<div id="hud3"><span id="h3s" class="pill"></span><span id="h3spark" class="pill" hidden>✨ 0</span><span id="h3c" role="status" aria-live="polite"></span></div>'); document.body.appendChild(hud);
  hud.querySelector('#h3s').textContent = `${T('Scene', 'Escena')} ${P.level}/${P.total}`;
  document.body.appendChild(el(`<a id="home" href="${addQ('gallery.html')}">🏠 ${T('Home', 'Inicio')}</a>`));
  const screen = (h, bg) => { const s = el(`<div class="scr off">${bg ? `<div class="bg" style="background-image:url('${bg}')"></div>` : ''}${h}</div>`); ps.appendChild(s); requestAnimationFrame(() => s.classList.remove('off')); return s; };
  const close = async s => { s.classList.add('off'); await sl(350); s.remove(); };
  const G = () => window.__GAME__;
  const STORY = {
    1: ['🦋', 'Three kids are lost in the playground, so collect them and open the magic door!', '¡Tres nenes se perdieron en el patio, así que juntalos y abrí la puerta mágica!'],
    2: ['☁️', 'The clouds block the path, so fly carefully between them!', '¡Las nubes tapan el camino, así que volá con cuidado entre ellas!'],
    3: ['☀️', 'This is the last flight, so carry the kids home to the sun!', '¡Este es el último vuelo, así que llevá a los nenes hasta el sol!']
  };
  function pickArt(s) {
    const rows = [[/mariposa|butterfly/i, '🦋'], [/nube|cloud/i, '☁️'], [/sol\b|sun\b/i, '☀️'], [/fantasma|ghost/i, '👻'], [/monstruo|monster/i, '👾'], [/estrella|star/i, '⭐'], [/hueso|bone/i, '🦴'], [/fuego|fire/i, '🔥'], [/agua|water/i, '💧'], [/castillo|castle/i, '🏰'], [/casa|house\b|home\b/i, '🏠'], [/gatito|kitten|gato|\bcat\b/i, '🐱'], [/perro|\bdog\b/i, '🐶'], [/drag/i, '🐉'], [/nave|\bship\b|rocket/i, '🚀'], [/piedra|rock/i, '🪨']];
    for (const [re, em] of rows) if (re.test(s)) return em;
    return '✨';
  }
  function oneLine(s) {
    s = String(s || '').replace(/\s+/g, ' ').trim().replace(/^[¡!?\s]+/, '');
    s = s.replace(/^(?:[A-Za-z]{2,14})!\s+/, '');
    const parts = s.split(/(?<=[.!])\s+/).map(x => x.trim()).filter(Boolean);
    let line = parts[0] || s;
    if (line.replace(/[.!]+$/, '').length < 28 && parts[1]) {
      const b = parts[1].replace(/[.!]+$/, '');
      const rest = /^I\b/.test(b) ? b : (b.charAt(0).toLowerCase() + b.slice(1));
      line = line.replace(/[.!]+$/, '') + ', ' + rest;
    }
    if (line.length > 140) line = line.slice(0, 136).replace(/\s+\S*$/, '') + '…';
    if (line && !/[.!?…]$/.test(line)) line += '!';
    return line;
  }
  function storyParts(n) {
    if (/playground_01/.test(B.sample || '') || !B.scene_intro) {
      const row = STORY[n] || STORY[1];
      return { art: row[0], line: T(row[1], row[2]) };
    }
    const src = String(B.scene_intro || '');
    const shown = ES ? src : tr(src);
    let line = oneLine(shown);
    if (!ES && LEAK.test(line)) line = oneLine(tr(P.scene || '')) || 'A new adventure is waiting for you!';
    if (!ES && LEAK.test(line)) line = 'A new adventure is waiting for you!';
    return { art: pickArt(src + ' ' + shown + ' ' + (P.scene || '')), line: line };
  }
  function swallowNextClick() {
    const shield = (e) => { e.preventDefault(); e.stopPropagation(); };
    window.addEventListener('pointerup', shield, true);
    window.addEventListener('click', shield, true);
    setTimeout(() => { window.removeEventListener('pointerup', shield, true); window.removeEventListener('click', shield, true); }, 800);
  }
  function story(parts) {
    clearTimeout(window.__TALE_TIMER__);
    const old = document.getElementById('tale'); if (old) old.remove();
    const art = parts.art || '✨', line = parts.line || '';
    const b = el(`<div id="tale" role="dialog" aria-label="${T('Story', 'Historia')}"><div class="card"><div class="kicker">${T('Story', 'Historia')}</div><div class="art" aria-hidden="true">${art}</div><p class="line">${esc(line)}</p><div class="hint">${T('Tap anywhere to skip', 'Tocá en cualquier lado para saltar')}</div></div></div>`);
    window.__TALE__ = { art: art, line: line, ms: 4000, at: Date.now(), closed: '', between: (P.level || 1) > 1, scene: P.level || 1 };
    const close = (how) => {
      if (!b.isConnected || b.dataset.bye) return;
      b.dataset.bye = '1';
      clearTimeout(window.__TALE_TIMER__);
      window.__TALE__.closed = how;
      if (how === 'tap') swallowNextClick();
      b.remove();
      try { revealPad(); } catch (e) {}
    };
    b.addEventListener('pointerdown', ev => { ev.preventDefault(); ev.stopPropagation(); close('tap'); });
    window.__TALE_TIMER__ = setTimeout(() => close('auto'), 4000);
    document.body.appendChild(b);
    try { syncModal(); } catch (e) {}
  }

  // procedural SFX (WebAudio, no assets) + mute toggle
  let AC = null, MUTED = q.get('mute') === '1' || localStorage.getItem('dj_mute') === '1';
  const tone = (f, d = .12, t = 'sine', v = .18, at = 0, f2) => { if (MUTED) return; try { AC = AC || new (window.AudioContext || window.webkitAudioContext)(); if (AC.state === 'suspended') AC.resume(); const o = AC.createOscillator(), g = AC.createGain(), n = AC.currentTime + at; o.type = t; o.frequency.setValueAtTime(f, n); if (f2) o.frequency.exponentialRampToValueAtTime(f2, n + d); g.gain.setValueAtTime(0, n); g.gain.linearRampToValueAtTime(v, n + .01); g.gain.exponentialRampToValueAtTime(.001, n + d); o.connect(g).connect(AC.destination); o.start(n); o.stop(n + d + .02); } catch (e) {} };
  const SFX = { collect: () => { tone(880, .09, 'triangle'); tone(1320, .14, 'triangle', .16, .07); }, spark: () => { tone(1046, .08, 'sine', .12); tone(1568, .16, 'triangle', .14, .06); tone(2093, .22, 'sine', .1, .12); }, door: () => { [523, 659, 784, 1047].forEach((f, i) => tone(f, .25, 'sine', .14, i * .08)); }, win: () => { [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, .35, 'triangle', .16, i * .1)); tone(1568, .6, 'sine', .12, .55); }, oops: () => tone(320, .35, 'sawtooth', .09, 0, 110), fix: () => { tone(600, .05, 'square', .06); tone(760, .05, 'square', .06, .09); tone(920, .05, 'square', .06, .18); }, scan: () => tone(1200, .05, 'sine', .05), ok: () => { tone(784, .12, 'triangle', .16); tone(1175, .3, 'triangle', .16, .1); }, lose: () => tone(300, .4, 'triangle', .12, 0, 150), tap: () => tone(660, .05, 'sine', .08) };
  // anti-stack: same cue at most once per 140ms; log every fired cue (window.__SFX_LOG__) for tests
  { const last = {}; window.__SFX_LOG__ = []; Object.keys(SFX).forEach(k => { const f = SFX[k]; SFX[k] = () => { const n = performance.now(); if (n - (last[k] || -1e9) < 140) return; last[k] = n; window.__SFX_LOG__.push(k + (MUTED ? ':muted' : '')); f(); }; }); }
  window.__SFX__ = SFX;
  const mb = el(`<button id="mu" aria-label="${T('Sound', 'Sonido')}">${MUTED ? '🔇' : '🔊'}</button>`); document.body.appendChild(mb);
  mb.onclick = () => { MUTED = !MUTED; localStorage.setItem('dj_mute', MUTED ? '1' : '0'); mb.textContent = MUTED ? '🔇' : '🔊'; SFX.tap(); };
  const pz = el(`<button id="pz" aria-label="${T('Pause', 'Pausa')}">⏸</button>`), pzo = el(`<div id="pzo"><div class="title">⏸ ${T('Paused', 'Pausa')}</div><div class="hint">${T('Tap the arrows or swipe to move. Pick everything up, then step into the door.', 'Tocá las flechas o deslizá para moverte. Juntá todo y entrá a la puerta.')}</div><button>▶ ${T('Keep playing', 'Seguir jugando')}</button><div class="row2"><button class="sm">↺ ${T('Start over', 'Empezar de nuevo')}</button><button class="sm" id="pzm"></button></div><a class="home" href="${addQ('gallery.html')}">🏠 ${T('Home', 'Inicio')}</a><a id="jt" href="${addQ('?judge=1')}">${T('Judge view', 'Vista jurado')}</a></div>`); document.body.append(pz, pzo);
  pz.onclick = () => { pzmT && pzmT(); pzo.classList.add('on'); window.__PAUSED__ = true; }; const [r1, r2] = pzo.querySelectorAll('button'), pzm = pzo.querySelector('#pzm'); const pzmT = () => pzm.textContent = MUTED ? T('🔇 Sound off', '🔇 Sonido apagado') : T('🔊 Sound on', '🔊 Sonido prendido'); pzmT(); pzm.onclick = () => { mb.onclick(); pzmT(); }; r1.onclick = () => { pzo.classList.remove('on'); window.__PAUSED__ = false; }; r2.onclick = () => { G() && G().reset(); r1.onclick(); };
  addEventListener('keydown', e => { if (e.key === 'Escape' || e.key === 'p') pzo.classList.contains('on') ? r1.onclick() : pz.onclick(); });
  // HUD + win/lose flow
  function noun(goals) { const s = (goals || []).map(g => ((g.label || '') + ' ' + (g.id || '')).toLowerCase()).join(' '), n = (goals || []).length || 1; const rows = [[/nene|nena/, 'kid', 'kids', n => n === 1 ? 'el nene' : `los ${n} nenes`], [/estrella|star/, 'star', 'stars', n => n === 1 ? 'la estrella' : `las ${n} estrellas`], [/hueso|bone/, 'bone', 'bones', n => n === 1 ? 'el hueso' : `los ${n} huesos`], [/c[ií]rculo/, 'circle', 'circles', n => n === 1 ? 'el círculo' : `los ${n} círculos`], [/flor/, 'flower', 'flowers', n => n === 1 ? 'la flor' : `las ${n} flores`], [/casa/, 'house', 'houses', n => n === 1 ? 'la casa' : `las ${n} casas`], [/drag[oó]n/, 'dragon friend', 'dragon friends', n => n === 1 ? 'el dragón amigo' : `los ${n} dragones amigos`], [/amigo/, 'friend', 'friends', n => n === 1 ? 'el amigo' : `los ${n} amigos`], [/punto/, 'dot', 'dots', n => n === 1 ? 'el punto' : `los ${n} puntos`], [/castillo/, 'castle', 'castles', n => n === 1 ? 'el castillo' : `los ${n} castillos`]]; for (const [re, a, b, es] of rows) if (re.test(s)) return { en: n === 1 ? a : b, es: es(n) }; return { en: n === 1 ? 'prize' : 'prizes', es: n === 1 ? 'el premio' : `los ${n} premios` }; }
  function objective(sp, S) { const goals = sp.goals || [], wc = sp.win_condition || {}; if (S.doorOpen && sp.door) return '🚪 ' + T('Walk into the glowing door.', 'Entrá a la puerta brillante.'); if (wc.type === 'collect_all' && goals.length) { const w = noun(goals); return '⭐ ' + T(goals.length === 1 ? `Collect the ${w.en}.` : `Collect all ${goals.length} ${w.en}.`, `Juntá ${w.es}.`); } const id = (wc.target || '') + ' ' + ((goals.find(g => g.id === wc.target) || goals[0] || {}).label || ''); if (wc.type === 'reach_goal') { if (/sol|sun/i.test(id)) return '☀️ ' + T('Reach the sun.', 'Llegá al sol.'); if (/hueso|bone/i.test(id)) return '🦴 ' + T('Reach the bone.', 'Llegá al hueso.'); if (/estrella|star/i.test(id)) return '⭐ ' + T('Reach the star.', 'Llegá a la estrella.'); if (/castillo|castle/i.test(id)) return '🏰 ' + T('Reach the castle.', 'Llegá al castillo.'); if (/casa|house/i.test(id)) return '🏠 ' + T('Reach the house.', 'Llegá a la casa.'); return '🎯 ' + T('Reach the goal.', 'Llegá a la meta.'); } if (wc.type === 'survive_seconds') return '🛡️ ' + T(`Stay safe for ${wc.seconds} seconds.`, `Aguantá ${wc.seconds} segundos.`); return tr(sp.title || ''); }
  function pipsFor(goals, n, pop) { return goals.map((_, j) => `<span class="pip${j < n ? ' on' : ''}${pop && j === n - 1 ? ' pop' : ''}" aria-hidden="true">⭐</span>`).join(''); }
  function paintBanner(h, text, pips, door) { h.classList.toggle('door', door); h.classList.remove('out'); h.classList.add('in'); h.innerHTML = `<span class="kicker">${esc(T('Goal', 'Meta'))}</span><span class="obj">${esc(text)}</span><span class="pips">${pips}</span>`; if (!REDUCED_MOTION) { h.style.animation = 'none'; void h.offsetWidth; h.style.animation = ''; } }
  function showCombo(n) {
    let c = document.getElementById('combo');
    if (!c) { c = document.createElement('div'); c.id = 'combo'; c.setAttribute('role', 'status'); document.body.appendChild(c); }
    c.innerHTML = '<b>×' + n + '</b> <small>' + T('Combo!', '¡Combo!') + '</small>';
    window.__JUICE__.combo = n;
    c.classList.remove('on'); void c.offsetWidth; c.classList.add('on'); c.style.opacity = '';
    clearTimeout(showCombo._t); clearTimeout(window.__COMBO_TIMER__);
    showCombo._t = window.__COMBO_TIMER__ = setTimeout(() => { if (window.__HOLD_COMBO__) return; if (c.isConnected) { c.classList.remove('on'); c.style.opacity = '0'; } }, REDUCED_MOTION ? 1600 : 4000);
  }
  function paintSpark() {
    const el = document.getElementById('h3spark'); if (!el) return;
    const plaza = /playground_01/.test((B && B.sample) || '');
    if (!plaza) { el.hidden = true; return; }
    el.hidden = false; el.textContent = '✨ ' + ((window.__RUN__ && window.__RUN__.stars) || 0);
  }
  function sparkPop() {
    let c = document.getElementById('sparkpop');
    if (!c) { c = document.createElement('div'); c.id = 'sparkpop'; c.setAttribute('role', 'status'); const host = document.getElementById('hud3'); if (!host) return; host.appendChild(c); }
    c.textContent = T('Bonus star!', '¡Estrella extra!');
    c.classList.add('on'); clearTimeout(sparkPop._t);
    sparkPop._t = setTimeout(() => { if (c.isConnected) c.classList.remove('on'); }, REDUCED_MOTION ? 900 : 1600);
  }
  function watchSpark() {
    paintSpark();
    const g = G(), spk = window.__SPARK__;
    if (!g || !spk || !spk.cell || !g.spec || !g.spec.player) return;
    let S; try { S = g.state(); } catch (e) { return; }
    if (!S || !S.player) return;
    const home = S.steps === 0 && S.status === 'playing' && S.player.x === g.spec.player.x && S.player.y === g.spec.player.y;
    if (home) { const r = window.__RUN__; spk.got = !!(r && r.got && r.got[spk.cell.id]); }
    if (!spk.got && S.status === 'playing' && S.player.x === spk.cell.x && S.player.y === spk.cell.y) {
      spk.got = true;
      const r = loadRun();
      if (r && !r.got[spk.cell.id]) { r.got[spk.cell.id] = 1; r.stars = (r.stars || 0) + 1; saveRun(r); }
      spk.score = (window.__RUN__ && window.__RUN__.stars) || 0;
      try { SFX.spark(); } catch (e) {}
      sparkPop(); paintSpark();
    }
  }
  function hookSpark() {
    const g = G(); if (!g || !g.move || g.__sparkHook) return !!g;
    const mv = g.move, rs = g.reset;
    g.move = function () { const r = mv.apply(this, arguments); try { watchSpark(); } catch (e) {} return r; };
    g.reset = function () { const out = rs.apply(this, arguments); window.__DS__ = 0; window.__DOOR_WALK__ = false; try { watchSpark(); } catch (e) {} return out; };
    g.__sparkHook = true; return true;
  }
  window.__WATCH_SPARK__ = watchSpark;
  const hookIv = setInterval(() => { if (hookSpark()) clearInterval(hookIv); }, 40);
  let done = false; setInterval(() => { try { watchSpark(); } catch (e) {} const g = G(); if (!g || !g.spec) return; const S = g.state(), sp = g.spec; const prevC = window.__VC__ || 0; if (S.collected.length < prevC) { window.__VC__ = S.collected.length; window.__COMBO_N__ = 0; window.__COMBO_AT__ = 0; } const delta = S.collected.length - (window.__VC__ || 0); const gained = delta > 0; if (gained) { const nowMs = performance.now(); const chain = (nowMs - (window.__COMBO_AT__ || 0)) <= 2800; const n = chain ? (window.__COMBO_N__ || 0) + delta : delta; window.__COMBO_N__ = n; window.__COMBO_AT__ = nowMs; window.__VC__ = S.collected.length; SFX.collect(); if (n >= 2) showCombo(n); if (!REDUCED_MOTION) try { navigator.vibrate && navigator.vibrate(40); } catch (e) {} } const h = document.getElementById('h3c'); if (h) { const goals = sp.goals || [], text = objective(sp, S), showPips = (sp.win_condition || {}).type === 'collect_all', pips = showPips ? pipsFor(goals, S.collected.length, gained) : '', sig = text + '|' + S.collected.length + '|' + (S.doorOpen ? 1 : 0), door = !!(S.doorOpen && sp.door); if (h.dataset.sig !== sig) { const textChanged = !!(h.dataset.text && text !== h.dataset.text); if (textChanged && !REDUCED_MOTION) { h._pend = { text, pips, door, sig }; if (!h.dataset.leaving) { h.dataset.leaving = '1'; h.classList.remove('in'); h.classList.add('out'); setTimeout(() => { const pnd = h._pend; if (!pnd || !h.isConnected) { delete h.dataset.leaving; return; } paintBanner(h, pnd.text, pnd.pips, pnd.door); h.dataset.sig = pnd.sig; h.dataset.text = pnd.text; delete h.dataset.leaving; }, 180); } } else if (textChanged || !h.dataset.text) { paintBanner(h, text, pips, door); h.dataset.sig = sig; h.dataset.text = text; } else { h.classList.toggle('door', door); const box = h.querySelector('.pips'); if (box) box.innerHTML = pips; else paintBanner(h, text, pips, door); h.dataset.sig = sig; } } }
    if (S.doorOpen && !window.__DS__) { window.__DS__ = 1; SFX.door(); }
    if (S.status === 'lost' && !done) { done = true; SFX.lose(); setTimeout(() => { g.reset(); done = false; }, 1400); }
    if (S.doorOpen && S.status === 'playing' && window.__AUTO_DOOR__ !== false && !window.__DOOR_WALK__ && window.__DEMO_PLAY_DONE__) walkDoor(g);
    if (S.status === 'won' && !done) { done = true; SFX.win(); setTimeout(next, 2200); } }, 150);
  async function walkDoor(g) { window.__DOOR_WALK__ = true; const sp = g.spec, D = sp.door, W = sp.grid.w, H = sp.grid.h, wall = new Set(); (sp.walls || []).forEach(w => { for (let i = 0; i < (w.w || 1); i++) for (let j = 0; j < (w.h || 1); j++) wall.add((w.x + i) + ',' + (w.y + j)); }); (sp.hazards || []).forEach(w => { for (let i = 0; i < (w.w || 1); i++) for (let j = 0; j < (w.h || 1); j++) wall.add((w.x + i) + ',' + (w.y + j)); });
    const S0 = g.state().player, prev = { [S0.x + ',' + S0.y]: null }, Q = [[S0.x, S0.y]]; while (Q.length) { const [x, y] = Q.shift(); if (x === D.x && y === D.y) break; for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const k = (x + dx) + ',' + (y + dy); if (x + dx < 0 || y + dy < 0 || x + dx >= W || y + dy >= H || wall.has(k) || k in prev) continue; prev[k] = [x, y, dx, dy]; Q.push([x + dx, y + dy]); } }
    const mv = []; let k = D.x + ',' + D.y; while (prev[k]) { const [x, y, dx, dy] = prev[k]; mv.unshift([dx, dy]); k = x + ',' + y; } for (const m of mv) { if (g.state().status !== 'playing') break; g.move(...m); await sl(180); } }
  function runStarCount(root, n) {
    n = Math.max(0, n | 0);
    const box = root.querySelector('#finale');
    const num = root.querySelector('#starn');
    const stars = box ? [...box.querySelectorAll('i.star')] : [];
    const yay = box ? box.querySelector('.yay') : null;
    const fin = { stars: n, shown: 0, sceneStars: 3, sceneShown: 0, done: false, ticked: false, reduced: !!REDUCED_MOTION };
    window.__FINALE__ = fin;
    const showAll = () => {
      fin.shown = n; fin.sceneShown = 3;
      if (num) num.textContent = String(n);
      stars.forEach(s => s.classList.add('on'));
      if (yay) yay.classList.add('on');
      if (box) box.classList.add('still');
    };
    if (REDUCED_MOTION) { showAll(); fin.done = true; return fin; }
    if (num) num.textContent = '0';
    let scene = 0;
    const popScene = () => {
      if (scene < 3) {
        if (stars[scene]) stars[scene].classList.add('on');
        scene += 1; fin.sceneShown = scene;
        try { SFX.spark(); } catch (e) {}
        setTimeout(popScene, 240);
        return;
      }
      let k = 0;
      const step = () => {
        if (k >= n) { fin.shown = n; fin.ticked = true; fin.done = true; if (num) num.textContent = String(n); if (yay) yay.classList.add('on'); return; }
        k += 1; fin.shown = k; fin.ticked = true;
        if (num) num.textContent = String(k);
        try { SFX.spark(); } catch (e) {}
        if (k >= n) { fin.done = true; if (yay) yay.classList.add('on'); } else setTimeout(step, 240);
      };
      setTimeout(step, 240);
    };
    setTimeout(popScene, 60);
    return fin;
  }
  function previewFinale(n) {
    let host = document.getElementById('finalePreview');
    if (!host) { host = document.createElement('div'); host.id = 'finalePreview'; host.hidden = true; host.setAttribute('aria-hidden', 'true'); document.body.appendChild(host); }
    const yay = esc(T('Three scenes clear!', '¡Tres escenas listas!'));
    const prefix = esc(T('Stars collected: ', 'Estrellas juntadas: '));
    const start = REDUCED_MOTION ? (n | 0) : 0;
    host.innerHTML = `<div id="finale" aria-hidden="true"><i class="star">⭐</i><i class="star">⭐</i><i class="star">⭐</i><span class="yay">${yay}</span></div><b>${prefix}<span id="starn">${start}</span></b>`;
    return runStarCount(host, n | 0);
  }
  window.__JUICE__.previewFinale = previewFinale;
  async function next() { if (!last) { fxLock('iris'); wipe.textContent = T("🚪 The door is waiting… let's go!", '🚪 ¡La puerta te está esperando… vamos!'); void wipe.offsetWidth; wipe.classList.add('on'); await sl(REDUCED_MOTION ? 40 : 900); const hold = +window.__HOLD_FX__ || 0; if (hold) await sl(Math.min(hold, 4000)); location.href = addQ(P.next + '?go=1'); return; }
    const run = loadRun() || { t0: Date.now(), stars: 0 };
    const ms = Math.max(0, Date.now() - (run.t0 || Date.now()));
    const secAll = Math.round(ms / 1000), mins = Math.floor(secAll / 60), secs = secAll % 60;
    const clock = mins + ':' + (secs < 10 ? '0' : '') + secs;
    const starsN = run.stars || 0;
    window.__RESULTS__ = { stars: starsN, ms: ms, time: clock };
    const timeLine = T('Time: ' + clock, 'Tiempo: ' + clock);
    const yay = esc(T('Three scenes clear!', '¡Tres escenas listas!'));
    const prefix = esc(T('Stars collected: ', 'Estrellas juntadas: '));
    const startN = REDUCED_MOTION ? starsN : 0;
    const s = screen(`<h1>${T('🌟 You did it! 🌟', '🌟 ¡Lo lograste! 🌟')}</h1><div class="msg">${T('What you drew is a real game now.<br>You beat all 3 scenes!', 'Lo que dibujaste ahora es un juego de verdad.<br>¡Pasaste las 3 escenas!')}</div><div id="finale" aria-hidden="true"><i class="star">⭐</i><i class="star">⭐</i><i class="star">⭐</i><span class="yay">${yay}</span></div><div id="results" role="status"><b>${prefix}<span id="starn">${startN}</span></b><b id="timeline">${esc(timeLine)}</b></div><div class="duo"><img src="${drawing}"><b>➜</b><img src="${hero}"></div><div class="msg" style="font-size:22px;opacity:.9">${T('What will you draw next? ✏️', '¿Qué vas a dibujar ahora? ✏️')}</div><button class="big">${T('Play again', 'Jugar de nuevo')}</button> <a class="big" href="${addQ('gallery.html')}" style="display:inline-block;margin-top:10px;color:#fff;text-decoration:none;opacity:.9">${T('🎨 See more games', '🎨 Ver más juegos')}</a>`, hero);
    s.querySelector('button').onclick = () => location.href = addQ(window.__FIRST__ || 'play.html'); runStarCount(s, starsN); setTimeout(() => confetti(s), REDUCED_MOTION ? 0 : 80); }
  function confetti(host) {
    const c = document.createElement('canvas'); c.id = 'winconfetti'; c.className = 'confetti'; c.setAttribute('aria-hidden', 'true');
    c.style.cssText = 'position:fixed;left:0;top:0;pointer-events:none;z-index:2147483646';
    const place = () => { c.style.width = innerWidth + 'px'; c.style.height = innerHeight + 'px'; };
    place(); addEventListener('resize', place);
    c.width = innerWidth; c.height = innerHeight; (host || document.body).appendChild(c);
    const x = c.getContext('2d'), cols = ['#ffd54f', '#ff8ac2', '#6fe3ff', '#7dffb0', '#fff6c2', '#c38bff', '#ff7043', '#ffffff'];
    const N = REDUCED_MOTION ? 42 : 220, shapes = ['rect', 'star', 'circle', 'ribbon'];
    window.__JUICE__.confetti = N; window.__JUICE__.shapes = shapes; window.__JUICE__.confettiReduced = !!REDUCED_MOTION;
    const P = Array.from({ length: N }, (_, i) => { const ang = (i / N) * 6.283, burst = i < N * .5; return { x: burst ? c.width * .5 : Math.random() * c.width, y: burst ? c.height * .38 : -16 - Math.random() * 80, vx: burst ? Math.cos(ang) * (2.2 + Math.random() * 6) : (Math.random() - .5) * 1.6, vy: burst ? Math.sin(ang) * 2.2 - 5 - Math.random() * 4 : 1.8 + Math.random() * 3.2, s: 8 + Math.random() * 14, r: Math.random() * 6, vr: (Math.random() - .5) * .22, c: cols[i % cols.length], sh: shapes[i % 4], g: .07 + Math.random() * .05 }; });
    const star = (cx, cy, r) => { x.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * .42 : r, px = cx + Math.cos(a) * rr, py = cy + Math.sin(a) * rr; i ? x.lineTo(px, py) : x.moveTo(px, py); } x.closePath(); x.fill(); };
    const draw = () => { x.clearRect(0, 0, c.width, c.height); for (const p of P) { x.save(); x.translate(p.x, p.y); x.rotate(p.r); x.fillStyle = p.c; if (p.sh === 'star') star(0, 0, p.s * .7); else if (p.sh === 'circle') { x.beginPath(); x.arc(0, 0, p.s * .38, 0, 6.28); x.fill(); } else if (p.sh === 'ribbon') { x.fillRect(-p.s * .15, -p.s * .7, p.s * .3, p.s * 1.4); } else x.fillRect(-p.s / 2, -p.s / 5, p.s, p.s * .42); x.restore(); } };
    if (REDUCED_MOTION) { P.forEach(p => { p.x = Math.random() * c.width; p.y = 24 + Math.random() * c.height * .72; p.vx = 0; p.vy = 0; }); draw(); return; }
    let t = 0; (function f() { for (const p of P) { p.vy += p.g; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.vx *= .992; if (p.y > c.height + 30) { p.y = -20; p.x = Math.random() * c.width; p.vy = 2 + Math.random() * 3; p.vx = (Math.random() - .5) * 1.5; } } draw(); if (++t < 480) requestAnimationFrame(f); else c.remove(); })();
  }
  window.__JUICE__.playConfetti = confetti;
  // touch: D-pad (gaps included), left-thumb soft analog stick, swipe + tap-to-move. No screen dead zones.
  const overlayOpen = () => !!(document.body.classList.contains('transitioning') || document.getElementById('onb') || document.getElementById('tale') || document.getElementById('demoNote') || (document.getElementById('wipe') && document.getElementById('wipe').classList.contains('on')) || (document.getElementById('pzo') && document.getElementById('pzo').classList.contains('on')) || (document.getElementById('gate') && document.getElementById('gate').classList.contains('on')) || document.querySelector('#ps .scr:not(.off)'));
  const busy = () => !!(window.__PAUSED__ || overlayOpen());
  function step(dx, dy) { if (busy() || !(dx || dy)) return; const g = G(); if (!g || !g.move) return; let S; try { S = g.state(); } catch (e) { return; } if (!S || S.status !== 'playing') return; g.move(dx, dy); }
  function toward(x, y) { const dx = x - innerWidth / 2, dy = y - innerHeight / 2; if (Math.abs(dx) < .5 && Math.abs(dy) < .5) return [0, -1]; return Math.abs(dx) >= Math.abs(dy) ? [Math.sign(dx) || 0, 0] : [0, Math.sign(dy) || 0]; }
  const dpad = el(`<div id="dpad" hidden><button type="button" class="u" data-d="0,-1" aria-label="${T('Up', 'Arriba')}">⬆️</button><button type="button" class="l" data-d="-1,0" aria-label="${T('Left', 'Izquierda')}">⬅️</button><button type="button" class="r" data-d="1,0" aria-label="${T('Right', 'Derecha')}">➡️</button><button type="button" class="d" data-d="0,1" aria-label="${T('Down', 'Abajo')}">⬇️</button></div>`);
  document.body.appendChild(dpad); dpad.addEventListener('contextmenu', e => e.preventDefault());
  const stick = el(`<div id="stick" hidden aria-hidden="true"><div class="ring"></div><div class="knob"></div></div>`);
  document.body.appendChild(stick);
  const knob = stick.querySelector('.knob');
  const DEAD = .2, MAXR = 46;
  let kx = 0, ky = 0, tx = 0, ty = 0, raf = 0, joy = null, rec = null, gap = null;
  function spring() { kx += (tx - kx) * .42; ky += (ty - ky) * .42; knob.style.transform = `translate3d(${kx.toFixed(1)}px,${ky.toFixed(1)}px,0)`; if (joy || Math.hypot(tx - kx, ty - ky) > .4) raf = requestAnimationFrame(spring); else { raf = 0; kx = ky = 0; knob.style.transform = 'translate3d(0,0,0)'; } }
  function kick() { if (!raf) raf = requestAnimationFrame(spring); }
  function padDir(x, y) { const r = dpad.getBoundingClientRect(); const dx = x - (r.left + r.width / 2), dy = y - (r.top + r.height / 2); if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return [0, -1]; return Math.abs(dx) >= Math.abs(dy) ? [Math.sign(dx) || 0, 0] : [0, Math.sign(dy) || 0]; }
  function axis4(ax, ay) { if (Math.abs(ax) < 1e-3 && Math.abs(ay) < 1e-3) return null; return Math.abs(ax) >= Math.abs(ay) ? [Math.sign(ax) || 0, 0] : [0, Math.sign(ay) || 0]; }
  function analog(cx, cy, px, py) { let dx = px - cx, dy = py - cy; const mag = Math.hypot(dx, dy); if (mag > MAXR && mag > 0) { dx *= MAXR / mag; dy *= MAXR / mag; } const m = Math.min(1, Math.hypot(dx, dy) / MAXR); tx = dx; ty = dy; kick(); if (m <= DEAD) return { ax: 0, ay: 0, out: 0 }; const out = (m - DEAD) / (1 - DEAD), h = Math.hypot(dx, dy) || 1; return { ax: dx / h * out, ay: dy / h * out, out }; }
  function placeStick(cx, cy) { const s = stick.offsetWidth || 140; const x = Math.max(s / 2 + 8, Math.min(innerWidth * .5 - 8, cx)); const y = Math.max(s / 2 + 8, Math.min(innerHeight - s / 2 - 8, cy)); stick.classList.add('float', 'hot'); stick.style.left = (x - s / 2) + 'px'; stick.style.top = (y - s / 2) + 'px'; return { x, y }; }
  function homeStick() { stick.classList.remove('float', 'hot'); stick.style.left = ''; stick.style.top = ''; tx = 0; ty = 0; kick(); }
  function releaseHold() { if (gap) { clearInterval(gap.iv); gap = null; } if (joy) { clearTimeout(joy.arm); clearTimeout(joy.iv); joy = null; homeStick(); window.__STICK__ = { x: 0, y: 0 }; } if (rec) { clearTimeout(rec.arm); if (rec.iv) clearInterval(rec.iv); rec = null; } }
  function syncModal() { const open = overlayOpen(); document.body.classList.toggle('modal-open', open); if (open) releaseHold(); }
  function leftThumb(x, y) { if (stick.hidden) return false; if (!dpad.hidden) { const r = dpad.getBoundingClientRect(); if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return false; } return x <= innerWidth * .5; }
  const ui = 'button,a,#dpad,#onb,#pzo,#ps,#pz,#mu,#skip,#tale,#gate,#home,#demoNote,input,label';
  dpad.querySelectorAll('button').forEach(btn => { const [dx, dy] = btn.dataset.d.split(',').map(Number); let iv = null, pid = null; const stop = e => { if (e && pid !== null && e.pointerId !== pid) return; if (iv) clearInterval(iv); iv = null; pid = null; }; btn.addEventListener('pointerdown', e => { if (pid !== null || (e.button && e.button !== 0)) return; e.preventDefault(); e.stopPropagation(); pid = e.pointerId; try { btn.setPointerCapture(e.pointerId); } catch (err) {} const go = () => step(dx, dy); go(); iv = setInterval(go, 180); }); btn.addEventListener('pointerup', stop); btn.addEventListener('pointercancel', stop); btn.addEventListener('lostpointercapture', stop); });
  const stopGap = e => { if (!gap || (e && gap && e.pointerId !== gap.id)) return; clearInterval(gap.iv); gap = null; };
  dpad.addEventListener('pointerdown', e => { if (gap || (e.button && e.button !== 0) || (e.target.closest && e.target.closest('button'))) return; e.preventDefault(); e.stopPropagation(); gap = { id: e.pointerId, x: e.clientX, y: e.clientY, iv: null }; try { dpad.setPointerCapture(e.pointerId); } catch (err) {} const go = () => { if (!gap) return; const d = padDir(gap.x, gap.y); if (d) step(d[0], d[1]); }; go(); gap.iv = setInterval(go, 180); });
  dpad.addEventListener('pointermove', e => { if (!gap || e.pointerId !== gap.id) return; gap.x = e.clientX; gap.y = e.clientY; });
  dpad.addEventListener('pointerup', stopGap); dpad.addEventListener('pointercancel', stopGap); dpad.addEventListener('lostpointercapture', stopGap);
  function endJoy(e) { if (!joy || (e && e.pointerId !== joy.id)) return; clearTimeout(joy.arm); clearTimeout(joy.iv); const tap = !joy.moved, pulsed = joy.pulsed, ax = joy.ax, ay = joy.ay, x = joy.x, y = joy.y; joy = null; homeStick(); window.__STICK__ = { x: 0, y: 0 }; if (!tap && !pulsed) { const d = axis4(ax, ay); if (d) step(d[0], d[1]); } else if (tap && !pulsed) { const d = toward(x, y); if (d) step(d[0], d[1]); } }
  function endRec(e) { if (!rec || (e && e.pointerId !== rec.id)) return; clearTimeout(rec.arm); if (rec.iv) clearInterval(rec.iv); if (!rec.swiped && !rec.held) { const d = toward(rec.x, rec.y); if (d) step(d[0], d[1]); } rec = null; }
  const showPad = () => { document.body.classList.add('touch'); window.__STICK__ = window.__STICK__ || { x: 0, y: 0 }; if (document.body.classList.contains('transitioning') || overlayOpen()) { dpad.hidden = true; stick.hidden = true; dpad.setAttribute('aria-disabled', 'true'); dpad.querySelectorAll('button').forEach(b => { b.disabled = true; }); syncModal(); return; } dpad.hidden = false; stick.hidden = false; dpad.removeAttribute('aria-disabled'); dpad.querySelectorAll('button').forEach(b => { b.disabled = false; }); syncModal(); }; try { if (matchMedia('(pointer: coarse)').matches || (navigator.maxTouchPoints || 0) > 0) showPad(); } catch (e) {}
  addEventListener('touchstart', () => showPad(), { once: true, passive: true });
  ['c', 'c3d', 'wrap', 'gamecard'].forEach(id => { const n = document.getElementById(id); if (n) n.style.touchAction = 'none'; });
  addEventListener('pointerdown', e => {
    if (!document.body.classList.contains('play') || (e.button && e.button !== 0) || joy || rec) return;
    if (e.target.closest && e.target.closest(ui)) return;
    e.preventDefault();
    const cap = t => { try { (t && t.setPointerCapture ? t : document.body).setPointerCapture(e.pointerId); } catch (err) {} };
    if (leftThumb(e.clientX, e.clientY)) {
      const c = placeStick(e.clientX, e.clientY);
      joy = { id: e.pointerId, cx: c.x, cy: c.y, x: e.clientX, y: e.clientY, ax: 0, ay: 0, out: 0, moved: false, pulsed: false, arm: null, iv: null };
      window.__STICK__ = { x: 0, y: 0 }; cap(e.target);
      const pulse = () => { if (!joy) return; joy.pulsed = true; const d = axis4(joy.ax, joy.ay) || (!joy.moved ? toward(joy.x, joy.y) : null); if (d) step(d[0], d[1]); };
      joy.arm = setTimeout(() => { if (!joy) return; pulse(); const loop = () => { if (!joy) return; pulse(); joy.iv = setTimeout(loop, Math.round(260 - Math.min(1, joy.out) * 140)); }; joy.iv = setTimeout(loop, Math.round(260 - joy.out * 140)); }, 160);
      return;
    }
    rec = { id: e.pointerId, x0: e.clientX, y0: e.clientY, x: e.clientX, y: e.clientY, swiped: false, held: false, iv: null, arm: null };
    cap(e.target);
    rec.arm = setTimeout(() => { if (!rec || rec.swiped) return; const d = toward(rec.x, rec.y); if (!d) return; rec.held = true; step(d[0], d[1]); rec.iv = setInterval(() => { if (!rec) return; const d2 = toward(rec.x, rec.y); if (d2) step(d2[0], d2[1]); }, 180); }, 180);
  });
  addEventListener('pointermove', e => {
    if (joy && e.pointerId === joy.id) { joy.x = e.clientX; joy.y = e.clientY; const a = analog(joy.cx, joy.cy, e.clientX, e.clientY); joy.ax = a.ax; joy.ay = a.ay; joy.out = a.out; if (a.out > 0) joy.moved = true; window.__STICK__ = { x: +a.ax.toFixed(3), y: +a.ay.toFixed(3) }; return; }
    if (!rec || e.pointerId !== rec.id || rec.swiped || rec.held) return;
    rec.x = e.clientX; rec.y = e.clientY;
    const dx = e.clientX - rec.x0, dy = e.clientY - rec.y0;
    if (Math.hypot(dx, dy) < 28) return;
    rec.swiped = true; clearTimeout(rec.arm); if (rec.iv) clearInterval(rec.iv);
    step(Math.abs(dx) >= Math.abs(dy) ? Math.sign(dx) : 0, Math.abs(dx) >= Math.abs(dy) ? 0 : Math.sign(dy));
  });
  addEventListener('pointerup', e => { endJoy(e); endRec(e); });
  addEventListener('pointercancel', e => { endJoy(e); endRec(e); });
  addEventListener('touchmove', e => { if (!document.body.classList.contains('play')) return; if (e.target.closest && e.target.closest('#ps .scr, #pzo, #gate, #onb, #tale, #demoNote, #home')) return; e.preventDefault(); }, { passive: false });
  try { const mo = new MutationObserver(() => syncModal()); mo.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] }); } catch (e) {}
  syncModal();
  addEventListener('gesturestart', e => { try { e.preventDefault(); } catch (err) {} });
  addEventListener('dblclick', e => { if (document.body.classList.contains('play')) e.preventDefault(); });
  addEventListener('keydown', e => { if (document.body.classList.contains('play') && ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) e.preventDefault(); });
  function showOnboard(done) { const finish = () => { if (done) done(); }; if (document.getElementById('onb')) { finish(); return; } try { if (localStorage.getItem('dj_onboard_v2') === '1') { finish(); return; } } catch (e) { finish(); return; } const b = el(`<div id="onb" role="dialog" aria-label="${T('How to play', 'Cómo jugar')}"><div class="card"><div class="kicker">${T('First time here', 'Primera vez')}</div><div>👆 ${T('Swipe, or tap the arrows, to move', 'Deslizá o tocá las flechas para moverte')}</div><div>⭐ ${T('Pick up every friend', 'Juntá a todos los amigos')}</div><div>🚪 ${T('Then walk into the glowing door', 'Después entrá a la puerta brillante')}</div><div class="go">${T('Tap anywhere to start', 'Tocá en cualquier lado para empezar')}</div></div></div>`); const dismiss = ev => { if (ev) { ev.preventDefault(); ev.stopPropagation(); } if (!b.isConnected) return; swallowNextClick(); try { localStorage.setItem('dj_onboard_v2', '1'); } catch (e) {} b.remove(); finish(); try { syncModal(); } catch (e2) {} }; b.addEventListener('pointerdown', dismiss); document.body.appendChild(b); try { syncModal(); } catch (e) {} }
  function beginPlay() { showOnboard(() => story(storyParts(P.level || 1))); }
  function showSavedDemo() { if (document.getElementById('demoNote')) return; const src = B.photo_src || (B.drawing_b64 ? 'data:image/png;base64,' + B.drawing_b64 : ''); const quote = B.transcript ? esc(tr(B.transcript)) : ''; const b = el(`<div id="demoNote" role="dialog" aria-label="${T('Saved demo', 'Demo guardada')}"><div class="card"><div class="line">${T('Playing a saved demo world (drawing + voice made earlier)', 'Jugando un mundo demo guardado (dibujo y voz hechos antes)')}</div>${src ? `<img alt="${T('Saved drawing', 'Dibujo guardado')}" src="${src}">` : ''}${quote ? `<div class="tr">“${quote}”</div>` : ''}<button type="button" class="big">${T('▶ Play', '▶ Jugar')}</button></div></div>`); let gone = false; const dismiss = ev => { if (gone) return; gone = true; if (ev) { ev.preventDefault(); ev.stopPropagation(); swallowNextClick(); } b.remove(); try { document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); } catch (e) {} beginPlay(); syncModal(); }; b.addEventListener('pointerdown', dismiss); document.body.appendChild(b); syncModal(); }
  function honestNote() { const offline = typeof navigator !== 'undefined' && navigator.onLine === false; return offline ? T('You are offline. No AI check ran. This page did not call a Meta API.', 'Estás sin conexión. No se hizo ninguna revisión con IA. Esta página no llamó a una API de Meta.') : T('No AI check ran. This page did not call a Meta API.', 'No se hizo ninguna revisión con IA. Esta página no llamó a una API de Meta.'); }
  // later scenes already skip the intro
  if (q.get('go') === '1' || P.level > 1) { fxLock(P.level % 2 === 0 ? 'wipe' : 'iris'); wipe.textContent = `${T('Scene', 'Escena')} ${P.level}${P.scene ? ': ' + tr(P.scene) : ''}`; wipe.style.transition = 'none'; wipe.classList.add('on'); requestAnimationFrame(() => setTimeout(() => { wipe.style.transition = ''; wipe.classList.remove('on'); beginPlay(); setTimeout(fxUnlock, REDUCED_MOTION ? 0 : 520); }, REDUCED_MOTION ? 40 : 700)); return; }
  // Gallery Play: saved demo, no upload, no recording, no fake check.
  if (q.get('create') !== '1') { showSavedDemo(); return; }
  // Optional local create. Nothing here is sent to an AI or a Meta API.
  (async () => {
    let s = screen(`<h1>${T('Playable Drawing', 'Dibujo Jugable')}</h1><div class="msg" style="font-size:22px;opacity:.85">${T('Draw it. Tell your game. Play it.', 'Dibujá. Contá tu juego. Jugalo.')}</div><button class="big">${T('▶ PLAY', '▶ JUGAR')}</button>`, hero);
    await new Promise(r => s.querySelector('button').onclick = r); try { document.documentElement.requestFullscreen && await document.documentElement.requestFullscreen(); } catch (e) {} await close(s);
    s = screen(`<div class="msg">${T('Add a drawing and a voice rule', 'Sumá un dibujo y una regla en voz')}</div><div class="drop"><label>📸<span>${T('Photo of the drawing', 'Foto del dibujo')}</span><input id="ph" type="file" accept="image/*"></label><label>🎙️<span>${T('Voice audio', 'Audio de voz')}</span><input id="au" type="file" accept="audio/*"></label></div><button type="button" class="big" id="mic">${T('🎙️ Record voice (audio only)', '🎙️ Grabar voz (solo audio)')}</button><div id="err" style="color:#ffb4b4;font-size:16px;max-width:520px;min-height:1.2em"></div><button class="big" id="go" disabled>${T('▶ Play', '▶ Jugar')}</button><div style="opacity:.85;font-size:15px;max-width:560px">${esc(honestNote())}</div>`);
    const err = s.querySelector('#err'), go = s.querySelector('#go'), ph = s.querySelector('#ph'), au = s.querySelector('#au');
    let photoOk = false, photo = '';
    ph.onchange = () => { const f = ph.files && ph.files[0]; photoOk = false; go.disabled = true; if (!f || !f.size) { err.textContent = T('That file is empty. Pick a photo of the drawing.', 'Ese archivo está vacío. Elegí una foto del dibujo.'); return; } if (!f.type || f.type.indexOf('image/') !== 0) { err.textContent = T('That is not an image. Pick a photo.', 'Eso no es una imagen. Elegí una foto.'); ph.value = ''; return; } photoOk = true; photo = URL.createObjectURL(f); const L = ph.parentNode; L.innerHTML = `<img src="${photo}" alt=""><span>${T('Photo ready', 'Foto lista')}</span>`; err.textContent = ''; go.disabled = false; };
    au.onchange = () => { const f = au.files && au.files[0]; if (!f || !f.size) { err.textContent = T('That audio file is empty.', 'Ese audio está vacío.'); return; } if ((f.type || '').indexOf('video/') === 0) { err.textContent = T('Video is not allowed. Voice has to be audio only.', 'El video no está permitido. La voz tiene que ser solo audio.'); au.value = ''; return; } if (f.type && f.type.indexOf('audio/') !== 0) { err.textContent = T('That is not an audio file.', 'Eso no es un archivo de audio.'); au.value = ''; return; } const span = au.parentNode.querySelector('span'); if (span) span.textContent = '🎵 ' + f.name.slice(0, 22); err.textContent = T('Audio file ready. It stays on this phone. ', 'Archivo de audio listo. Se queda en este teléfono. ') + honestNote(); };
    s.querySelector('#mic').onclick = async () => { err.textContent = ''; if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { err.textContent = T('This browser cannot record audio. Pick an audio file instead. ', 'Este navegador no puede grabar audio. Elegí un archivo de audio. ') + honestNote(); return; } let stream = null; try { stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false }); } catch (e) { err.textContent = T('Microphone was blocked. Pick an audio file instead. ', 'El micrófono está bloqueado. Elegí un archivo de audio. ') + honestNote(); return; } const videoTracks = stream.getVideoTracks ? stream.getVideoTracks() : []; videoTracks.forEach(t => t.stop()); if (videoTracks.some(t => t.readyState === 'live')) { stream.getTracks().forEach(t => t.stop()); err.textContent = T('The camera turned on, so recording was stopped. Voice has to be audio only. ', 'Se prendió la cámara, así que se detuvo la grabación. La voz tiene que ser solo audio. ') + honestNote(); return; } const audioTracks = stream.getAudioTracks ? stream.getAudioTracks() : []; if (!audioTracks.length) { stream.getTracks().forEach(t => t.stop()); err.textContent = T('No microphone track. Nothing was recorded. ', 'No hay pista de micrófono. No se grabó nada. ') + honestNote(); return; } let chunks = []; const mime = (window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported('audio/webm')) ? 'audio/webm' : ''; let rec = null; try { rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream); } catch (e) { rec = null; } if (!rec) { stream.getTracks().forEach(t => t.stop()); err.textContent = T('Audio-only microphone opened, then closed. Nothing was uploaded. ', 'Se abrió el micrófono solo de audio y se cerró. No se subió nada. ') + honestNote(); return; } rec.ondataavailable = ev => { if (ev.data && ev.data.size) chunks.push(ev.data); }; rec.onstop = () => { stream.getTracks().forEach(t => t.stop()); const blob = new Blob(chunks, { type: rec.mimeType || 'audio/webm' }); if (!blob.size || (blob.type || '').indexOf('video/') === 0) { err.textContent = T('That recording was empty or was not audio. ', 'Esa grabación estaba vacía o no era audio. ') + honestNote(); return; } const url = URL.createObjectURL(blob); const old = s.querySelector('#clip'); if (old) old.remove(); const clip = document.createElement('audio'); clip.id = 'clip'; clip.controls = true; clip.src = url; s.appendChild(clip); err.textContent = T('Voice saved on this phone (audio only, no video). Nothing was uploaded. ', 'Voz guardada en este teléfono (solo audio, sin video). No se subió nada. ') + honestNote(); }; try { rec.start(); } catch (e) { stream.getTracks().forEach(t => t.stop()); err.textContent = T('Could not start the audio recording. ', 'No se pudo empezar la grabación de audio. ') + honestNote(); return; } s.querySelector('#mic').textContent = T('🎙️ Listening…', '🎙️ Escuchando…'); setTimeout(() => { try { if (rec.state === 'recording') rec.stop(); } catch (e) {} }, 1600); };
    go.onclick = async () => { if (!photoOk) { err.textContent = T('Add a real photo of the drawing first. ', 'Primero sumá una foto de verdad del dibujo. ') + honestNote(); return; } await close(s); const s2 = screen(`<div class="msg">${esc(honestNote())}</div><div class="msg" style="font-size:18px;opacity:.9">${T('Your photo stays on this phone. The world you play is the saved demo.', 'Tu foto se queda en este teléfono. El mundo que jugás es el demo guardado.')}</div><div class="stage"><img src="${photo}" alt=""></div><button class="big">${T('▶ Play', '▶ Jugar')}</button>`); await new Promise(r => s2.querySelector('button').onclick = r); await close(s2); beginPlay(); };
  })();
})();
