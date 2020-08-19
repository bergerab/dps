* Ideas
** Index
   Actions table will tell you to setup a data source.

** Add Data Source Screen
   Add URL, port, username, password, and database to use.

   Support InfluxDB, Timescale.
   
** Add Data Screen
   Specify the data source to use, along with a date range, other
   query fields. If there are no data sources you can upload a CSV to use.

   Choose a system that the test is for, and map the test data to
   system signal names.

   TODO: what if there are two tests needed for a signal KPI?

** Create KPI Screen
   Custom language to create KPIs.

   Specify signal input names, and configuration input names, and
   produce an output value with some name.

   Signal input names is something like "Va" or "Vb" or "Ia".

   Configuration input names is something like "Crated".

   (THD needs parameters for the HZ/base frequency)

#+BEGIN_SRC lisp
(average
  (with-window 1 second
    (+ Va Vb Vc)))
#+END_SRC

The language would be a barebones LISP with the following forms:
#+BEGIN_SRC lisp
  ;; Top-level keywords

  (require-kpi load-percent) ;; require some KPI
  (require-signal Va Vb Vc Ia Ib Ic) ;; require signals
  (require-constant crated) ;; define constants

  (define-kpi kpi-name ;; define a KPI
      "KPI Display Name"

    ;; The following are only allowed within "define-kpi"
    ;; They are all operators who operate on signals

    ;; Basic arithmetic operators
    (+ a b c) ;; Signal Number -> Signal Number -> Signal Number
    (- a b c)
    (* a b c)
    (/ a b c)
    (sqrt a)

    ;; Basic comparison operators
    (= a b)
    (!= a b)
    (> a b)
    (< a b)
    (>= a b)
    (<= a b)

    ;; Choice
    (if a b c) ;; Signal Boolean -> Signal a -> Signal a -> Signal a

    ;; Logical operators
    (and a b) ;; Signal Boolean -> Signal Boolean -> Signal Boolean
    (or a b)

    ;; You can create a window based on time
    (with-window ;; Number -> Unit -> Signal Number -> Signal (Window Number)
	x units
	(+ a b c))
    ;; TODO: it might be nice to have
    ;; (with-hopping-window ...)
    ;; (with-sliding-window ...)

    ;; Operators that can be applied to windows
    (average *window*) ;; Signal (Window Number) -> Signal Number
    (median *window*)
    (mode *window*)
    (max *window*)
    (min *window*)

    ;; Special built-in calculations
    (thd a ;; Signal Number -> Signal Number
	 :something-else 9
	 :fundamental-frequency 60))
#+END_SRC

This way you can express any KPI that we need in this language and
modifying them would be easy.

Or I could use some sort of "query-builder" style thing.

** Add System Screen
   Specify signal names, and constants for the system.

   Specify available KPIs by hooking up signal names to KPI inputs.



** Batch Process Screen
   There should be a link for each System. For example, the inverter would
   have a link. 
   
   When you click a link, it will have a table for all the KPIs that
   have been added for that System.

   There will be a single dropdown on the page to choose which test
   data to use. If the test data is missing some signal required for
   any KPI, those KPIs should be grayed out. If no KPIs have their
   dependent KPIs available, they too should be grayed out.


** Another way to do it

Define KPIs without defining which data it is for.

So you would define power as (Va*Ia + Vb*Ib + Vc*Ic) and save that.

Then when you start a batch process.

#+BEGIN_SRC scheme
(define (efficiency Va Vb Vc Ia Ib Ic)
        (+ (* Va Ia) (* Vb Ib) (* Vc Ic)))
#+END_SRC

Best way to do it is to keep the input signals in the UI, and the
computation in code mirror.

#+BEGIN_SRC scheme
(+ Va Vb Vc)
#+END_SRC

#+BEGIN_SRC scheme
(+ Va Vb Vc)
#+END_SRC


* Need to be able to do streaming from this too

* Home Page
Actions table.

Checklist:
    Setup Database Connection -> Systems -> 
  
* KPI Page
- Add input signal names (note these could be other KPIs -- backend will
have to resolve that)
- Add constant names

* System Page
  - Define a system which is a set of signal names, constants, and KPI
mappings.

* Data Sources Page
- Select a database connection, (optional) date range, and a table (for
influx it would be a measurement), allow for custom filter query too.

- Select a system the data source is for.

- Define mappings from data source signals to system signals.

* Batch Process Page
Choose a system, a list of available data sources should come
up. Choose from a checklist of KPIs to compute, and signals to
include in the output. 

* Stream Process Page
Choose a system, a list of available data sources should come
up. Choose which KPIs to compute and which signals to include in the
output. It will start a streaming task in the background.
