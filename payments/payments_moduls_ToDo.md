# Flujo de suscripción mensual

1. El usuario entra a la aplicación.

2. El usuario crea una cuenta.

3. El usuario crea una empresa.

4. El usuario queda asignado automáticamente como **Owner** de la empresa.

5. El sistema crea una `Subscription` con estado **PENDING**.

6. El usuario visualiza el catálogo de módulos disponibles.

7. El usuario selecciona los módulos que desea contratar.

8. El backend recibe la lista de IDs de los módulos.

9. El sistema busca cada módulo en la base de datos.

10. Se calcula la mensualidad sumando el precio (`price`) de todos los módulos seleccionados.

11. Se guarda temporalmente en `Subscription`:

* `status = PENDING`
* `amount = total calculado`
* `moduls = [1, 2, 4, 7]` (solo para saber qué módulos asignar cuando llegue el webhook).

12. Se crea la suscripción en AbacatePay utilizando el monto calculado.

13. AbacatePay devuelve la URL del checkout.

14. El usuario accede al checkout y realiza el primer pago.

15. AbacatePay envía un webhook confirmando el pago.

16. El backend valida el webhook.

17. Si el pago fue aprobado:

* Se ejecuta `assign_modules(company_id, module_ids)`.
* Se crean los registros en `Moduls_Companies`.
* `Subscription.status` cambia a `ACTIVE`.
* `Subscription.is_active = True`.
* Se establecen `current_period_start` y `current_period_end`.
* Opcionalmente, se limpia el campo temporal `moduls`.

18. Desde ese momento, el Owner y todos los empleados de esa empresa pueden utilizar únicamente los módulos contratados.

19. Cada vez que un usuario acceda a un módulo:

* Se verifica que la empresa tenga una suscripción activa.
* Se verifica que el módulo esté asignado a la empresa.

20. Al finalizar el período de facturación, AbacatePay realiza automáticamente un nuevo cobro utilizando el valor almacenado en `Subscription.amount`.

21. Si un pago mensual falla:

* El webhook actualiza la suscripción (`PAST_DUE`, `CANCELED`, etc.).
* `is_active` pasa a `False`.
* Las dependencias (`require_module`) comienzan a bloquear el acceso a todos los módulos hasta que el pago sea regularizado.
