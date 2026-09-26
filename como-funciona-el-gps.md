---
slug: como-funciona-el-gps
title: Cómo funciona el GPS (y por qué necesita la teoría de la relatividad)
dek: Tu móvil sabe dónde estás midiendo el tiempo que tardan en llegar señales desde satélites a 20.000 kilómetros. Sin las correcciones de Einstein, el error crecería kilómetros cada día.
category: tecnologia
date: 2026-09-09
image: gps
keywords: GPS, satélites, relatividad, Einstein, Galileo, geolocalización, relojes atómicos
related: cables-submarinos-internet, dia-en-venus, teclado-qwerty
---
Abrir un mapa en el móvil y ver un punto azul que marca tu posición parece lo más normal del mundo. Detrás de ese gesto hay una red de satélites, relojes atómicos y un problema físico que solo se resuelve teniendo en cuenta la teoría de la relatividad. Vamos a ver cómo encaja todo.

## Una red de relojes en el cielo

El sistema GPS (Sistema de Posicionamiento Global) pertenece a Estados Unidos. El primer satélite se lanzó en 1978 y el sistema se declaró plenamente operativo en 1995. Hoy lo forman unos treinta satélites que giran a unos **20.200 kilómetros** de altura, repartidos en seis planos orbitales para que desde casi cualquier punto de la Tierra haya varios a la vista.

:::dato {~12 horas} Lo que tarda cada satélite en dar una vuelta a la Tierra
Cada satélite GPS completa una órbita en algo menos de 12 horas, así que pasa dos veces al día por el cielo de cualquier lugar.
:::

Lo esencial de cada satélite no es su cámara ni su antena, sino su **reloj atómico**. Los satélites emiten continuamente una señal de radio que dice, en esencia: "soy tal satélite, estoy en tal posición y este mensaje salió a tal hora exacta".

## Medir distancias con el tiempo

Tu teléfono no envía nada a los satélites. Solo escucha. Cuando recibe una señal, compara la hora de salida con la hora de llegada. Como las ondas de radio viajan a la velocidad de la luz, unos 300.000 kilómetros por segundo, ese retraso indica la distancia al satélite.

Con la distancia a un satélite sabes que estás en algún punto de una esfera imaginaria centrada en él. Con dos, en la intersección de dos esferas, que es un círculo. Con tres, el círculo se reduce a dos puntos, y uno de ellos suele estar en el espacio o bajo tierra, así que se descarta. A este método se le llama **trilateración**.

:::nota
**¿Por qué hacen falta al menos cuatro satélites?** El reloj de tu móvil no es atómico y comete pequeños errores. La cuarta señal permite calcular ese error a la vez que la posición. En la práctica, los receptores usan todos los satélites que pueden captar para afinar el resultado.
:::

## El problema de la precisión

La luz recorre unos **30 centímetros en un nanosegundo** (una milmillonésima de segundo). Por eso, un error de solo una millonésima de segundo en los relojes se traduce en unos 300 metros de error en la posición. El GPS necesita relojes que no se desvíen más que unos pocos nanosegundos. Y aquí entra Einstein.

## Relatividad en órbita

La física del siglo XX descubrió que el tiempo no pasa igual para todos. Los relojes de los satélites se ven afectados por dos efectos opuestos:

1. **Relatividad especial.** Los satélites se mueven a unos 14.000 km/h respecto al suelo. Un reloj en movimiento rápido marcha más despacio: los relojes GPS se retrasan unos **7 microsegundos al día**.
2. **Relatividad general.** Cuanto más débil es la gravedad, más deprisa pasa el tiempo. A 20.000 kilómetros de altura, la gravedad terrestre es mucho menor, y los relojes se adelantan unos **45 microsegundos al día**.

El efecto neto es que los relojes de los satélites se adelantan unos **38 microsegundos cada día** respecto a los de la superficie.

:::dato {~10 km} Error diario sin corregir la relatividad
Treinta y ocho microsegundos parecen nada, pero multiplicados por la velocidad de la luz equivalen a más de 11 kilómetros. Sin corrección, los errores de posición se acumularían a un ritmo de unos 10 kilómetros al día.
:::

La solución es elegante: antes del lanzamiento, los relojes se ajustan para que en tierra funcionen ligeramente más despacio de lo debido. En lugar de oscilar a 10,23 megahercios, se configuran a 10,22999999543. Una vez en órbita, la relatividad los acelera justo lo necesario. El GPS es probablemente la aplicación cotidiana más clara de la teoría de Einstein.

## Por qué hoy es mucho más preciso

Hasta el 2 de mayo de 2000, Estados Unidos degradaba intencionadamente la señal civil mediante la llamada "disponibilidad selectiva", y la precisión rondaba los 100 metros. Al desactivarla, pasó a ser de unos pocos metros. Hoy los móviles combinan además varias fuentes:

- **Otros sistemas de satélites:** el europeo **Galileo**, el ruso GLONASS y el chino BeiDou. Galileo tiene uno de sus centros de servicio en Torrejón de Ardoz, en Madrid.
- **Ayudas desde la red (A-GPS):** el operador proporciona al móvil datos sobre qué satélites buscar, lo que acelera mucho la primera ubicación.
- **Redes wifi y antenas de telefonía,** muy útiles en ciudades donde los edificios bloquean o reflejan la señal.
- **Sensores del teléfono,** como el acelerómetro o la brújula, que ayudan a estimar el movimiento entre dos lecturas.

## Mucho más que mapas

Aunque lo asociamos a la navegación, uno de los usos más importantes del GPS es dar **la hora exacta**. Las redes eléctricas, las antenas de telefonía móvil y muchos sistemas financieros sincronizan sus relojes con estas señales. Por eso los países consideran la navegación por satélite una infraestructura crítica, y por eso Europa quiso tener su propio sistema independiente.

## Conclusión

Cada vez que miras tu ubicación en el móvil, tu teléfono está resolviendo un problema de geometría en tres dimensiones con la ayuda de relojes que corrigen el paso del tiempo según la relatividad. Es un recordatorio de que la física que parecía más abstracta hace un siglo sostiene hoy objetos de uso diario. Si te interesa la infraestructura invisible que nos conecta, no te pierdas cómo viaja internet [[cables-submarinos-internet|por cables en el fondo del mar]].

:::fuentes
- GPS.gov. "Space Segment" y "GPS Accuracy". Gobierno de Estados Unidos.
- Ashby, N. (2003). "Relativity in the Global Positioning System". *Living Reviews in Relativity*, 6.
- Agencia de la Unión Europea para el Programa Espacial (EUSPA). Información sobre Galileo y el Centro de Servicios GNSS.
:::
