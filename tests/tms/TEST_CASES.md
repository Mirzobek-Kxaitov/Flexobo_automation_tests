# TMS Test Cases

---

## Modul 1: Partnership (Delegations) — `/tms/delegations`

### Smoke

```
TC-P-001: Delegations sahifasi ochilishi
- Precondition: Broker sifatida login
- Steps: /tms/delegations sahifasiga o'tish
- Expected: Partners, Incoming, Sent, History tablari ko'rinadi
- Rol: broker, carrier, load_owner, owner_operator
- Prioritet: P0
```

```
TC-P-002: Delegations sahifasi company_driver uchun yopiq
- Precondition: company_driver sifatida login
- Steps: /tms/delegations ga to'g'ridan-to'g'ri o'tish
- Expected: Sahifa ko'rinmaydi yoki redirect bo'ladi
- Rol: company_driver
- Prioritet: P0
```

### Partnership CRUD

```
TC-P-010: Partner invite yuborish
- Precondition: Broker login, accepted partner yo'q
- Steps:
  1. "Invite partner" tugmasini bosish
  2. Partner turini tanlash (owner_operator)
  3. Partnerni tanlash
  4. "Send invitation" bosish
- Expected: Sent tabda invite ko'rinadi, status "pending"
- Rol: broker, carrier, load_owner
- Prioritet: P0
```

```
TC-P-011: Partner invite qabul qilish
- Precondition: Owner_operator login, incoming invite bor
- Steps:
  1. Incoming tabga o'tish
  2. Invite ni topish
  3. "Accept" bosish
- Expected: Partners tabda yangi partner ko'rinadi, status "accepted"
- Rol: owner_operator, broker, carrier
- Prioritet: P0
```

```
TC-P-012: Partner invite rad etish
- Precondition: Incoming invite mavjud
- Steps: "Decline" bosish
- Expected: Invite yo'qoladi, inviter ga notification boradi
- Rol: owner_operator, broker, carrier
- Prioritet: P0
```

```
TC-P-013: Sent invite ni cancel qilish
- Precondition: Sent invite mavjud, hali accept qilinmagan
- Steps: Sent tabda inviteni topib "Cancel" bosish
- Expected: Invite yo'qoladi
- Rol: broker, carrier, load_owner
- Prioritet: P1
```

```
TC-P-014: Partnership cancel qilish — active order yo'q
- Precondition: Accepted partner bor, aktiv delegated order yo'q
- Steps: Partners tabda "Cancel partnership" bosish
- Expected: Partnership bekor bo'ladi, partner yo'qoladi
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-P-015: Partnership cancel BLOCKED — active order bor
- Precondition: Accepted partner bor, aktiv delegated order mavjud
- Steps: "Cancel partnership" bosish
- Expected: Button disabled yoki xato xabar: "Cancel locked"
- Rol: broker, carrier
- Prioritet: P0
```

### Negative

```
TC-P-020: User partner faqat owner_operator bo'lishi kerak
- Precondition: Invite dialog ochiq
- Steps: Company_driver ni partner sifatida tanlashga urinish
- Expected: Company_driver option ro'yxatda yo'q
- Rol: broker, carrier
- Prioritet: P1
```

```
TC-P-021: History tabda o'tgan invitelar ko'rinishi
- Precondition: Oldingi invite/accept/decline/cancel amallar bajarilgan
- Steps: History tabga o'tish
- Expected: Barcha o'tgan amallar tarixi ko'rinadi
- Rol: broker, carrier
- Prioritet: P2
```

---

## Modul 2: Orders Workbench — `/tms/orders`

### Smoke

```
TC-O-001: Orders sahifasi ochilishi
- Precondition: Broker login
- Steps: /tms/orders sahifasiga o'tish
- Expected: Order jadval ko'rinadi: Order, Type, Route, Price, Status, Actions
- Rol: broker, carrier, load_owner, owner_operator
- Prioritet: P0
```

```
TC-O-002: Filter chiplar ishlashi
- Precondition: Orders sahifasida
- Steps: "All", "Needs action", "Delegation offers", "Pending evaluation" chiplarini bosish
- Expected: Filtrlangan orderlar ko'rinadi
- Rol: broker, carrier
- Prioritet: P1
```

### Order ko'rish

```
TC-O-010: Direct order ko'rish
- Precondition: Booking orqali yaratilgan order mavjud
- Steps: Order qatoridagi "Open" bosish
- Expected: Order detail dialog ochiladi: Info, Map, Negotiations, History, Delegation tablari
- Rol: broker, carrier, load_owner
- Prioritet: P0
```

```
TC-O-011: Delegated order badge ko'rinishi
- Precondition: Delegated order mavjud
- Steps: Orders listni ko'rish
- Expected: "Delegated order" badge ko'rinadi, currentPartner ko'rsatiladi
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-O-012: Middle partner faqat View ko'radi
- Precondition: A→B→C chain da B sifatida login (B middle partner)
- Steps: Orderni ko'rish
- Expected: Faqat "View" button ko'rinadi, "Act" yo'q
- Rol: broker (middle)
- Prioritet: P0
```

### Order detail

```
TC-O-020: Info tab — route va status ko'rinishi
- Precondition: Order detail ochiq
- Steps: Info tabni ko'rish
- Expected: Status rail, route (From→To), price, current partner, driverTransport ko'rinadi
- Rol: broker, carrier, load_owner
- Prioritet: P0
```

```
TC-O-021: Delegation tab ko'rinishi (YANGI)
- Precondition: Delegated order detail ochiq
- Steps: Delegation tabni bosish
- Expected: Chain (source → Partner A → Partner B current), visible price, negotiation tarixi
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-O-022: History tab — status o'zgarishlar tarixi
- Precondition: Order detail ochiq
- Steps: History tabni bosish
- Expected: Status o'zgarishlar tarixi ko'rinadi (timestamp, actor, old→new)
- Rol: broker, carrier, load_owner
- Prioritet: P1
```

---

## Modul 3: Order Delegation (Offer / Negotiate)

### Delegate to partner

```
TC-D-001: Order ni partnerga delegatsiya qilish
- Precondition: Broker login, currentPartner, accepted partner bor
- Steps:
  1. Orderda "Delegate order" bosish
  2. Partner tanlash (accepted partner)
  3. Price, terms kiritish
  4. "Send delegation" bosish
- Expected: Delegation offer yaratildi, receiver ga notification boradi
- Rol: broker, carrier (currentPartner bo'lganida)
- Prioritet: P0
```

```
TC-D-002: Delegation offer qabul qilish
- Precondition: Owner_operator login, incoming delegation offer bor
- Steps:
  1. Orders da "Review offer" bosish
  2. "Accept" bosish
- Expected: Order delegated bo'ladi, currentPartner o'zgaradi
- Rol: owner_operator, broker, carrier
- Prioritet: P0
```

```
TC-D-003: Delegation offer rad etish
- Precondition: Incoming delegation offer bor
- Steps: "Decline" bosish
- Expected: Offer yopiladi, sender ga notification boradi, order o'zgarmaydi
- Rol: owner_operator, broker, carrier
- Prioritet: P0
```

```
TC-D-004: Counter price yuborish
- Precondition: Incoming delegation offer bor
- Steps:
  1. "Counter" bosish
  2. Yangi narx kiritish
  3. Yuborish
- Expected: Negotiation tarixiga yangi qadam qo'shiladi, currentPartner O'ZGARMAYDI
- Rol: owner_operator, broker, carrier
- Prioritet: P0
```

```
TC-D-005: Counter ni qabul qilish (sender tomonidan)
- Precondition: Counter yuborilgan, sender login
- Steps: "Accept counter" bosish
- Expected: Order delegated bo'ladi, receiver currentPartner bo'ladi
- Rol: broker, carrier
- Prioritet: P0
```

### Negative

```
TC-D-010: Middle partner delegate qila olmaydi
- Precondition: A→B→C chain, B (middle) login
- Steps: "Delegate order" ni qidirish
- Expected: Button yo'q yoki disabled
- Rol: broker (middle)
- Prioritet: P0
```

```
TC-D-011: Accepted partnerga faqat delegate mumkin
- Precondition: Delegate dialog ochiq
- Steps: Partner ro'yxatini ko'rish
- Expected: Faqat accepted partnerlar ko'rinadi
- Rol: broker, carrier
- Prioritet: P1
```

```
TC-D-012: Shipment boshlagandan keyin delegate mumkin emas
- Precondition: Order status "on_loading_site" yoki "enroute"
- Steps: Delegate amalini qidirish
- Expected: Delegate button yo'q
- Rol: broker, carrier
- Prioritet: P0
```

---

## Modul 4: Price Visibility

```
TC-PV-001: Partner A faqat o'z edge narxini ko'radi
- Precondition: A→B→C chain, A login
- Steps: Order detail ochish
- Expected: A→B narx ko'rinadi, B→C narx YASHIRIN
- Rol: A (broker/load_owner)
- Prioritet: P0
```

```
TC-PV-002: Partner C faqat B→C narxini ko'radi
- Precondition: A→B→C chain, C login (owner_operator)
- Steps: Order detail ochish
- Expected: B→C narx ko'rinadi, A→B narx YASHIRIN
- Rol: C (owner_operator)
- Prioritet: P0
```

```
TC-PV-003: Partner B ikkala edge narxini ko'radi
- Precondition: A→B→C chain, B login
- Steps: Order detail ochish
- Expected: A→B va B→C narxlari ko'rinadi
- Rol: B (broker/carrier)
- Prioritet: P0
```

```
TC-PV-004: Company driver narx ko'rmaydi
- Precondition: Company driver login, assigned order bor
- Steps: Order ko'rish
- Expected: Hech qanday narx ko'rinmaydi
- Rol: company_driver
- Prioritet: P0
```

```
TC-PV-005: Owner_operator marketplace narxini ko'rmaydi (delegated)
- Precondition: Delegated order, OO login
- Steps: Order detail ochish
- Expected: Faqat offered payout ko'rinadi, original marketplace narx yashirin
- Rol: owner_operator
- Prioritet: P1
```

---

## Modul 5: Order Handling Evaluation

```
TC-E-001: Delivered orderda "Evaluate" action ko'rinishi
- Precondition: Order "delivered" statusda
- Steps: Orders listda delivered orderni topish
- Expected: "Evaluate handling" button/action ko'rinadi
- Rol: broker, carrier, load_owner, owner_operator
- Prioritet: P0
```

```
TC-E-002: Evaluation dialog — rating va comment
- Precondition: Delivered order, "Evaluate" bosish
- Steps:
  1. Rating tanlash (1-5)
  2. Tags tanlash (On time, Documents ok, etc.)
  3. Comment yozish
  4. "Submit" bosish
- Expected: Evaluation saqlandi, "Evaluate" button yo'qoladi
- Rol: broker, carrier, load_owner, owner_operator
- Prioritet: P0
```

```
TC-E-003: Bidirectional evaluation — har bir tomon alohida baholaydi
- Precondition: A→B chain, A delivered qildi
- Steps: A login — B ni baholaydi, B login — A ni baholaydi
- Expected: Har biri mustaqil baholash amalga oshiradi
- Rol: A va B
- Prioritet: P0
```

```
TC-E-004: Delivered bo'lmagan orderda evaluate yo'q
- Precondition: Order "assigned" yoki "enroute" statusda
- Steps: Order action menusini ko'rish
- Expected: "Evaluate" action yo'q
- Rol: broker, carrier
- Prioritet: P1
```

```
TC-E-005: Middle partner faqat o'z direct edge ni baholaydi
- Precondition: A→B→C chain, B login
- Steps: B baholash dialog
- Expected: B faqat A ni va C ni baholaydi (2 ta alohida evaluation), A→C ni baholay olmaydi
- Rol: B (middle)
- Prioritet: P1
```

---

## Modul 6: Status Lifecycle va Locks

### Status o'tish

```
TC-S-001: booked → assigned (driverTransport assign)
- Precondition: Booked order, currentPartner login
- Steps: driverTransport assign qilish
- Expected: Status "assigned" ga o'tadi
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-S-002: assigned → on_loading_site (start execution)
- Precondition: Assigned order, load + driverTransport bor
- Steps: Status "on_loading_site" ga o'zgartirish
- Expected: Shipment boshlandi, status o'zgaradi
- Rol: broker, carrier, owner_operator
- Prioritet: P0
```

```
TC-S-003: To'liq lifecycle: booked → delivered
- Precondition: Yangi order
- Steps: booked → assigned → on_loading_site → enroute → on_delivery_site → delivered
- Expected: Har bir qadam muvaffaqiyatli o'tadi
- Rol: broker, carrier
- Prioritet: P0
```

### Locks

```
TC-S-010: Capacity yo'q — start blocked
- Precondition: driverTransport boshqa aktiv orderda band
- Steps: "on_loading_site" ga o'tishga urinish
- Expected: "Cannot start" dialog chiqadi, start blocked
- Rol: carrier, owner_operator
- Prioritet: P0
```

```
TC-S-011: Active orderdagi load o'zgartirib bo'lmaydi
- Precondition: Order "on_loading_site" yoki "enroute"
- Steps: Load ni almashtirshga urinish
- Expected: Amal blocked
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-S-012: Delivered va cancelled — terminal, o'zgartirib bo'lmaydi
- Precondition: Order "delivered" yoki "cancelled"
- Steps: Status o'zgartirishga urinish
- Expected: Status o'zgartirish mumkin emas
- Rol: broker, carrier
- Prioritet: P0
```

```
TC-S-013: Reject before shipment — faqat currentPartner
- Precondition: Order "booked" yoki "assigned", currentPartner login
- Steps: "Reject before start" bosish
- Expected: Order reject bo'ladi, oldingi partner ga notification boradi
- Rol: broker, carrier, owner_operator
- Prioritet: P0
```

```
TC-S-014: Reject — middle partner QILA OLMAYDI
- Precondition: A→B→C chain, A (middle) login
- Steps: "Reject" ni qidirish
- Expected: Button yo'q
- Rol: A (middle partner)
- Prioritet: P0
```

```
TC-S-015: Shipment boshlagandan keyin cancel mumkin emas
- Precondition: Order "on_loading_site" yoki "enroute"
- Steps: "Cancel" ni qidirish
- Expected: Cancel yo'q, faqat incident/dispute flow
- Rol: broker, carrier
- Prioritet: P0
```

---

## E2E Scenariylar

```
TC-E2E-001: To'liq delegation flow
- Steps:
  1. Load_owner load yaratadi
  2. Carrier bid qo'yadi, load_owner accept qiladi → order yaratiladi
  3. Carrier partneri (OO) ga delegate qiladi (price bilan)
  4. OO accept qiladi → currentPartner o'zgaradi
  5. OO o'z transportini assign qiladi
  6. OO statusni delivered gacha olib boradi
  7. Carrier va OO bir-birini baholaydi
- Expected: To'liq flow muvaffaqiyatli ishlaydi
- Rollar: load_owner, carrier, owner_operator
- Prioritet: P0
```

```
TC-E2E-002: Multi-step delegation chain
- Steps:
  1. Load_owner → Broker A (booking)
  2. Broker A → Carrier B (delegation)
  3. Carrier B → OO C (delegation)
  4. OO C executes → delivered
  5. Load_owner↔Broker A, Broker A↔Carrier B, Carrier B↔OO C baholashadi
- Expected: Chain to'g'ri ishlaydi, price har bir edge uchun alohida
- Rollar: load_owner, broker, carrier, owner_operator
- Prioritet: P1
```
