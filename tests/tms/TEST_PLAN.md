# TMS Test Plan

## 1. Maqsad

TMS (Transport Management System) yangi feature — delegation, partnership, order lifecycle,
price visibility, va evaluation — uchun to'liq test qamrovi.

---

## 2. Test qamrovi (Scope)

### Modullar

| # | Modul | Prioritet | Holati |
|---|-------|-----------|--------|
| 1 | Partnership (Delegations) | P0 | YANGI sahifa |
| 2 | Orders workbench | P0 | KENGAYTIRILGAN |
| 3 | Order delegation (offer/negotiate) | P0 | YANGI |
| 4 | Price visibility | P1 | YANGI |
| 5 | Order handling evaluation | P1 | YANGI |
| 6 | Status lifecycle va locks | P0 | KENGAYTIRILGAN |
| 7 | Fleet (Truck/Trailer) | P2 | MAVJUD (testlar yozilgan) |
| 8 | Drivers | P2 | MAVJUD |

### Rollar

| Rol | Partnership | Order | Delegation | Evaluation | Fleet | Drivers |
|-----|-------------|-------|------------|------------|-------|---------|
| load_owner | ✓ | ✓ | ✓ (cheklangan) | ✓ | ✗ | ✗ |
| broker | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| carrier | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| owner_operator | ✓ | ✓ | ✓ (qabul qilish) | ✓ | ✓ (faqat o'zi) | ✗ |
| company_driver | ✗ | ✓ (faqat ko'rish) | ✗ | ✗ | ✗ | ✗ |

---

## 3. Test turlari

### 3.1 Smoke testlar
- Har bir sahifaga kirish mumkinligi
- Asosiy CRUD operatsiyalar

### 3.2 Funksional testlar
- Har bir modul uchun batafsil test caseler
- Har bir rol uchun ruxsat/taqiq tekshiruvi

### 3.3 Cross-user testlar
- Bir foydalanuvchi yaratgan order/partnership boshqasiga ko'rinishi
- Price visibility — faqat o'z edge narxini ko'rishi

### 3.4 Negative testlar
- Ruxsat yo'q bo'lgan amallar (middle partner reject qila olmasligi)
- Capacity yo'q bo'lganda start qila olmaslik
- Active order bo'lganda partnership cancel qila olmaslik

### 3.5 E2E testlar
- To'liq flow: booking → delegation → execution → delivered → evaluation

---

## 4. Test muhiti

- **Framework:** Playwright + Python + POM
- **Rollar:** 4 ta test user (broker, load_owner, carrier, owner_operator)
- **URL:** APP_URL (.env dan)
- **CI:** GitHub Actions (headless)

---

## 5. Sahifalar va URL lar

| Sahifa | URL | Status |
|--------|-----|--------|
| Fleet | /tms/fleet | Mavjud |
| Drivers | /tms/drivers | Mavjud |
| Orders | /tms/orders | Kengaytiriladi |
| Delegations | /tms/delegations | YANGI |
| Order detail | /tms/orders/:id | Kengaytiriladi |
| Profile/Roles | /profile/root > Roles | Mavjud |
| Profile/Users | /profile/root > Users | Mavjud |

---

## 6. Risklarlar

| Risk | Ta'siri | Yechim |
|------|---------|--------|
| Usage/fleet limit | Testlar fail bo'ladi | Har test boshida reset yoki cleanup |
| Yangi sahifalar hali tayyor emas | Test yozib bo'lmaydi | Backend tayyor bo'lganda boshlash |
| Cross-user testlar sekin | CI timeout | Parallel execution, selective test run |

---

## 7. Test case tuzilishi

Har bir test case quyidagi formatda:

```
TC-XXX: [Test nomi]
- Precondition: ...
- Steps: ...
- Expected: ...
- Rol: ...
- Prioritet: P0/P1/P2
```
