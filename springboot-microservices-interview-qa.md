# Top 50 Spring Boot & Microservices Interview Questions (with Answers)

These questions run from Spring Boot basics up to microservices architecture. Answers are based on **Spring Boot 3.x+ and Java 17+** (`jakarta.*` packages). Code examples use the same names as the labs in this repo (`STUDENT-MS`, Eureka, API Gateway).

> **How to answer in an interview:** give a one-line definition, then explain **why** it exists, then give a short **example**. Interviewers care more about trade-offs than memorised definitions.

## Contents

1. [Spring Boot Fundamentals](#1-spring-boot-fundamentals) — Q1–Q14
2. [REST APIs and Spring MVC](#2-rest-apis-and-spring-mvc) — Q15–Q21
3. [Data Access and Transactions](#3-data-access-and-transactions) — Q22–Q27
4. [Security and Testing](#4-security-and-testing) — Q28–Q30
5. [Microservices Concepts](#5-microservices-concepts) — Q31–Q38
6. [Spring Cloud Building Blocks](#6-spring-cloud-building-blocks) — Q39–Q44
7. [Consistency, Observability and Deployment](#7-consistency-observability-and-deployment) — Q45–Q50

---

## 1. Spring Boot Fundamentals

### Q1. What is Spring Boot, and how is it different from the Spring Framework?

The **Spring Framework** is the core platform: the IoC container, dependency injection, AOP, Spring MVC, transactions, and data access. It is powerful, but you have to do a lot of the setup yourself.

**Spring Boot** sits on top of Spring. It lets you build stand-alone, production-ready apps with very little configuration ("convention over configuration").

| | Spring Framework | Spring Boot |
|---|---|---|
| Configuration | Mostly manual (Java config / XML) | Auto-configuration with sensible defaults |
| Dependencies | You pick and align versions | Starters + managed versions |
| Server | Deploy a WAR to an external server | Embedded Tomcat/Jetty, run with `java -jar` |
| Production features | Add them yourself | Actuator: health, metrics, info |

> **One-liner:** Spring Boot = Spring Framework + auto-configuration + starters + embedded server + production-ready features.

### Q2. What does `@SpringBootApplication` do?

It is a shortcut for three annotations:

- `@SpringBootConfiguration`: marks the class as a source of bean definitions (a specialised `@Configuration`).
- `@EnableAutoConfiguration`: turns on auto-configuration (Q3).
- `@ComponentScan`: scans this class's package **and all sub-packages** for components.

```java
@SpringBootApplication
public class StudentApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudentApplication.class, args);
    }
}
```

Because of component scanning, put the main class in the **root package** (e.g. `com.tcs.student`). Beans outside that package tree won't be found unless you set `scanBasePackages`.

`SpringApplication.run()` creates the `ApplicationContext`, applies auto-configuration, starts the embedded server, and then calls any `CommandLineRunner`/`ApplicationRunner` beans.

### Q3. How does auto-configuration work?

1. `@EnableAutoConfiguration` loads candidate configuration classes listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` inside the Boot jars (before Boot 2.7 this list lived in `spring.factories`).
2. Each class has **conditions** on it and only applies when they match:

| Condition | Applies when… |
|---|---|
| `@ConditionalOnClass` | a given class is on the classpath |
| `@ConditionalOnMissingBean` | you have **not** defined that bean yourself |
| `@ConditionalOnProperty` | a property has a given value |
| `@ConditionalOnWebApplication` | the app is a web application |

**Example:** H2 is on the classpath and there is no `DataSource` bean, so Boot creates an embedded `DataSource`. If you define your own `DataSource`, Boot steps aside and uses yours.

- **To see what was applied,** run with `--debug` to print the *condition evaluation report*, or call `/actuator/conditions`.
- **To exclude one,** use `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`.

### Q4. What are Spring Boot starters?

Starters are ready-made dependency bundles. Add one and you get everything a feature needs, in versions that work together.

| Starter | Brings in |
|---|---|
| `spring-boot-starter-web` | Spring MVC, Jackson, embedded Tomcat |
| `spring-boot-starter-data-jpa` | Spring Data JPA, Hibernate, HikariCP |
| `spring-boot-starter-validation` | Jakarta Bean Validation (Hibernate Validator) |
| `spring-boot-starter-security` | Spring Security |
| `spring-boot-starter-actuator` | Health, metrics, monitoring endpoints |
| `spring-boot-starter-test` | JUnit Jupiter, Mockito, AssertJ, Spring Test |

`spring-boot-starter-parent` (or the Boot BOM) manages the versions, so you normally leave out `<version>` for these dependencies.

### Q5. What are IoC and Dependency Injection? Which type of injection is preferred?

- **IoC (Inversion of Control):** your code doesn't create its collaborators with `new`. The Spring container creates, wires, and manages these objects (beans) for you.
- **DI (Dependency Injection):** the way IoC is done. An object's dependencies are handed to it from outside.

There are three styles: **constructor**, **setter**, and **field** (`@Autowired` on a field).

**Constructor injection is preferred** because:
- dependencies can be `final` (immutable and never null)
- required dependencies are explicit
- you can unit test with plain `new` plus mocks, without starting Spring
- circular dependencies fail fast at startup

```java
@Service
public class OrderService {
    private final PaymentClient paymentClient;

    public OrderService(PaymentClient paymentClient) { // single constructor → no @Autowired needed
        this.paymentClient = paymentClient;
    }
}
```

### Q6. `@Component` vs `@Service` vs `@Repository` vs `@Controller`?

All four are stereotype annotations. `@Service`, `@Repository`, and `@Controller` are specialisations of `@Component`, so component scanning picks up all of them.

| Annotation | Layer | Extra behaviour |
|---|---|---|
| `@Component` | Generic bean | — |
| `@Service` | Business logic | None today; documents intent |
| `@Repository` | Data access | Translates persistence exceptions into Spring's `DataAccessException` hierarchy |
| `@Controller` / `@RestController` | Web | Handler methods are detected by Spring MVC |

### Q7. What bean scopes are available?

| Scope | Instances |
|---|---|
| `singleton` (default) | One per Spring container |
| `prototype` | A new one every time it is requested |
| `request` | One per HTTP request |
| `session` | One per HTTP session |
| `application` | One per `ServletContext` |
| `websocket` | One per WebSocket session |

- **Singleton does not mean thread-safe.** Every request thread shares the same instance, so keep singletons stateless (no mutable instance fields).
- **Prototype inside a singleton** is injected only once. If you need a fresh instance each time, use `ObjectProvider<T>` or `@Lookup`.

### Q8. Explain the Spring bean lifecycle.

1. Instantiate (constructor)
2. Inject dependencies (setters/fields)
3. `Aware` callbacks (`BeanNameAware`, `ApplicationContextAware`, …)
4. `BeanPostProcessor#postProcessBeforeInitialization`
5. Initialise: `@PostConstruct` → `InitializingBean#afterPropertiesSet` → custom `initMethod`
6. `BeanPostProcessor#postProcessAfterInitialization`. AOP proxies (e.g. for `@Transactional`) are created here.
7. Bean is ready to use
8. On shutdown: `@PreDestroy` → `DisposableBean#destroy` → custom `destroyMethod`

Spring does **not** call destroy callbacks on prototype beans. The code that asked for them is responsible for cleaning them up.

```java
@Component
public class CacheWarmer {
    @PostConstruct void load()  { /* warm up cache */ }
    @PreDestroy    void close() { /* release resources */ }
}
```

### Q9. Two beans implement the same interface. How does Spring choose?

With no hint, injection fails with `NoUniqueBeanDefinitionException`. Your options:

- **`@Primary`** on one bean makes it the default choice.
- **`@Qualifier("beanName")`** at the injection point picks one explicitly. It wins over `@Primary`.
- **Inject them all** as `List<PaymentGateway>` or `Map<String, PaymentGateway>` (key = bean name). This works well for the strategy pattern.

```java
@Service @Primary   class UpiPayment  implements PaymentGateway { }
@Service("card")    class CardPayment implements PaymentGateway { }

public CheckoutService(@Qualifier("card") PaymentGateway gateway) { ... }
```

### Q10. How do profiles and externalised configuration work?

Configuration lives in `application.properties` or `application.yml`. The keys are the same; YAML is just hierarchical. Profile-specific files override the base file: `application-dev.yml`, `application-prod.yml`.

- **Activate a profile:** `spring.profiles.active=dev`, the env var `SPRING_PROFILES_ACTIVE=prod`, or `--spring.profiles.active=prod`.
- **Create beans only for a profile:** `@Profile("dev")`.

**Precedence** (simplified, highest wins):
1. Command-line arguments (`--server.port=9090`)
2. Java system properties (`-Dserver.port=9090`)
3. OS environment variables (`SERVER_PORT=9090`)
4. Profile-specific files (`application-{profile}.yml`)
5. `application.properties` / `application.yml`

Config files outside the jar override the ones packaged inside it. So the **same jar runs in every environment**, and only the config changes.

### Q11. `@Value` vs `@ConfigurationProperties`?

| | `@Value` | `@ConfigurationProperties` |
|---|---|---|
| Best for | One-off values | A group of related properties |
| Type safety | Per field | Whole typed object (class or record) |
| Relaxed binding (`max-size` ↔ `MAX_SIZE`) | Limited | Full |
| Validation | No | Yes, with `@Validated` |
| SpEL expressions | Yes | No |

```java
@Value("${app.welcome:Hello}")   // default value after the colon
private String welcome;

@ConfigurationProperties(prefix = "app.mail")
public record MailProperties(String host, int port, boolean ssl) { }
// register with @ConfigurationPropertiesScan on the main class
```

### Q12. What is Spring Boot Actuator?

Actuator (`spring-boot-starter-actuator`) adds production-ready endpoints for monitoring and managing the app.

| Endpoint | Shows |
|---|---|
| `/actuator/health` | UP/DOWN, including DB, disk, and broker checks |
| `/actuator/info` | App info (version, git commit) |
| `/actuator/metrics` | JVM, HTTP, and connection-pool metrics (Micrometer) |
| `/actuator/prometheus` | Metrics in Prometheus format (needs `micrometer-registry-prometheus`) |
| `/actuator/loggers` | View or change log levels at runtime |
| `/actuator/env`, `/beans`, `/mappings` | Config, beans, URL mappings |

By default **only `health` is exposed over HTTP**. Expose others deliberately, and secure them:

```properties
management.endpoints.web.exposure.include=health,info,metrics,prometheus
management.endpoint.health.show-details=when-authorized
```

### Q13. How does the embedded server work, and how do you change it?

`spring-boot-starter-web` includes an embedded Tomcat. The app is packaged as an executable "fat" jar with the server inside it, so `java -jar app.jar` is all you need. There's no external server and no WAR deployment.

- **Change the port:** `server.port=8081`
- **Use a random free port:** `server.port=0`. This is handy for running several instances behind Eureka.
- **Switch to Jetty:** exclude Tomcat and add the Jetty starter:

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
  <exclusions>
    <exclusion>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-tomcat</artifactId>
    </exclusion>
  </exclusions>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

### Q14. `CommandLineRunner` vs `ApplicationRunner`?

Both run **once, right after the application context has started**. They're useful for seeding data, warm-ups, and startup checks.

- `CommandLineRunner.run(String... args)` gets the raw arguments.
- `ApplicationRunner.run(ApplicationArguments args)` gets parsed arguments, e.g. `args.getOptionValues("mode")` for `--mode=batch`.

If you have several runners, order them with `@Order`.

```java
@Bean
CommandLineRunner seed(StudentRepository repo) {
    return args -> repo.save(new Student("Asha", "asha@example.com"));
}
```

---

## 2. REST APIs and Spring MVC

### Q15. `@Controller` vs `@RestController`?

- **`@Controller`** returns a **view name**, which is resolved to a template (Thymeleaf, JSP) to render HTML on the server. To return data instead, add `@ResponseBody`.
- **`@RestController`** = `@Controller` + `@ResponseBody` on every method. The return value goes straight into the response body, serialised to JSON by an `HttpMessageConverter` (Jackson).

### Q16. `@PathVariable` vs `@RequestParam` vs `@RequestBody`?

| Annotation | Reads from | Typical use | Example |
|---|---|---|---|
| `@PathVariable` | URI path | Identify a resource | `GET /students/42` |
| `@RequestParam` | Query string / form | Filter, sort, page; often optional | `GET /students?city=Pune&page=0` |
| `@RequestBody` | Request body (JSON) | Create/update payload | `POST /students` |

```java
@GetMapping("/students/{id}")
public StudentResponse get(@PathVariable Long id) { ... }

@GetMapping("/students")
public List<StudentResponse> search(@RequestParam(required = false) String city,
                                    @RequestParam(defaultValue = "0") int page) { ... }

@PostMapping("/students")
public ResponseEntity<StudentResponse> create(@Valid @RequestBody CreateStudentRequest req) { ... }
```

### Q17. Explain the request flow in Spring MVC.

```
Client
 → Embedded Tomcat
 → Servlet filters (including the Spring Security filter chain)
 → DispatcherServlet (front controller)
     → HandlerMapping: which controller method matches this URL + HTTP method?
     → HandlerInterceptor.preHandle()
     → HandlerAdapter: resolves arguments (@PathVariable, @RequestBody via
       HttpMessageConverter, @Valid) and invokes the method
         → Controller → Service → Repository → Database
     → Return value → HttpMessageConverter → JSON
     → HandlerInterceptor.postHandle() / afterCompletion()
 → Response to client
```

If any of this throws an exception, the `HandlerExceptionResolver`s handle it. That's where `@ExceptionHandler` and `@RestControllerAdvice` come in (Q19).

### Q18. Which HTTP methods and status codes should a REST API use? What is idempotency?

| Method | Purpose | Success status | Idempotent? |
|---|---|---|---|
| GET | Read | 200 OK | Yes (and safe) |
| POST | Create | 201 Created + `Location` header | No |
| PUT | Replace the whole resource | 200 OK / 204 No Content | Yes |
| PATCH | Partial update | 200 OK | Not guaranteed |
| DELETE | Remove | 204 No Content | Yes |

Common error codes:

| Code | Meaning |
|---|---|
| 400 Bad Request | Validation failed |
| 401 Unauthorized | Not authenticated |
| 403 Forbidden | Authenticated but not allowed |
| 404 Not Found | Resource doesn't exist |
| 409 Conflict | e.g. a duplicate |
| 500 Internal Server Error | Unhandled failure on the server |
| 503 Service Unavailable | Server temporarily can't handle the request |

**Idempotent** means sending the same request again leaves the server in the same state as sending it once. This matters because clients and gateways **retry** on timeouts.

Use `ResponseEntity` to control the status, headers, and body:

```java
@PostMapping("/students")
public ResponseEntity<StudentResponse> create(@Valid @RequestBody CreateStudentRequest req) {
    StudentResponse saved = service.create(req);
    return ResponseEntity.created(URI.create("/students/" + saved.id())).body(saved);
}
```

### Q19. How do you implement global exception handling?

Use `@RestControllerAdvice` (= `@ControllerAdvice` + `@ResponseBody`) with `@ExceptionHandler` methods. This puts the exception-to-response mapping in **one place**, so every error has the same shape and controllers stay clean.

```java
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) { super(message); }
}

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Validation failed");
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getFieldErrors()
          .forEach(fe -> errors.put(fe.getField(), fe.getDefaultMessage()));
        pd.setProperty("errors", errors);
        return pd;
    }
}
```

`ProblemDetail` (Spring 6 / Boot 3+) implements the standard RFC 9457 "problem details" error format, with the fields `type`, `title`, `status`, `detail`, and `instance`. To use it for Spring's built-in exceptions too, set `spring.mvc.problemdetails.enabled=true`.

### Q20. How do you validate request data?

1. Add `spring-boot-starter-validation`.
2. Put Jakarta Bean Validation constraints on the DTO fields.
3. Put `@Valid` on the `@RequestBody` parameter.

```java
public record CreateStudentRequest(
        @NotBlank String name,
        @NotBlank @Email String email,
        @Min(18) @Max(60) int age) { }
```

- An invalid body throws `MethodArgumentNotValidException`, which becomes a **400**. Customise the response in your advice (Q19).
- **Common constraints:** `@NotNull`, `@NotEmpty`, `@NotBlank`, `@Size`, `@Email`, `@Pattern`, `@Min`/`@Max`, `@Positive`, `@Past`/`@Future`.
- **`@NotNull` vs `@NotEmpty` vs `@NotBlank`** (a classic question):
  - `@NotNull`: not null.
  - `@NotEmpty`: not null and size > 0.
  - `@NotBlank`: not null and has at least one non-whitespace character (strings only).
- **Nested objects:** put `@Valid` on the nested field.
- **Path and query params:** constraints on `@PathVariable`/`@RequestParam` are also validated. Spring 6.1+ does this natively; older versions need `@Validated` on the controller class.

### Q21. What is a DTO, and why not just return entities?

A **DTO (Data Transfer Object)** is a plain object, often a Java `record`, shaped for the API and kept separate from the JPA entity.

Why use one:
- **Decoupling:** you can change the DB schema without breaking API clients, and the reverse.
- **Security:** fields like `password` or internal flags never leak.
- **No serialisation surprises:** returning entities directly can cause lazy-loading exceptions or infinite recursion on bidirectional relationships.
- **Fit for purpose:** use separate *request* DTOs (what a client may send) and *response* DTOs (what you show).

You can map by hand or with **MapStruct**.

```java
public record StudentResponse(Long id, String name, String email) {
    public static StudentResponse from(Student s) {
        return new StudentResponse(s.getId(), s.getName(), s.getEmail());
    }
}
```

---

## 3. Data Access and Transactions

### Q22. JPA vs Hibernate vs Spring Data JPA?

| | What it is |
|---|---|
| **JPA** (Jakarta Persistence) | A **specification**: annotations (`@Entity`, `@Id`, `@OneToMany`), `EntityManager`, and JPQL. It has no implementation of its own. |
| **Hibernate** | The most popular JPA **implementation** (ORM provider), and the default in Spring Boot. It generates the SQL and manages the persistence context and caching. |
| **Spring Data JPA** | A Spring **abstraction on top of JPA**. You write a repository interface and Spring generates the implementation. |

> **Analogy:** JPA is the interface, Hibernate is the class that implements it, and Spring Data JPA writes your DAO boilerplate for you.

### Q23. `CrudRepository` vs `JpaRepository`? How do derived queries and `@Query` work?

- **`CrudRepository<T, ID>`** provides basic CRUD: `save`, `findById`, `findAll`, `deleteById`, `count`, `existsById`.
- **`JpaRepository<T, ID>`** has all of that, plus paging/sorting and JPA-specific methods (`flush`, `saveAndFlush`, batch deletes, `getReferenceById`). It returns `List` rather than `Iterable`. This is the one most projects use.

**Derived query methods:** Spring builds the query from the method name.

```java
public interface StudentRepository extends JpaRepository<Student, Long> {

    Optional<Student> findByEmail(String email);
    List<Student> findByCityAndAgeGreaterThan(String city, int age);
    List<Student> findByNameContainingIgnoreCaseOrderByNameAsc(String text);
    boolean existsByEmail(String email);

    // JPQL: uses entity and field names, not table/column names
    @Query("SELECT s FROM Student s WHERE s.department.name = :dept")
    List<Student> findByDepartment(@Param("dept") String dept);

    // Native SQL
    @Query(value = "SELECT * FROM students WHERE active = true", nativeQuery = true)
    List<Student> findActiveNative();

    // Update/delete queries need @Modifying and must run inside a transaction
    @Modifying
    @Query("UPDATE Student s SET s.active = false WHERE s.lastLogin < :date")
    int deactivateInactive(@Param("date") LocalDate date);
}
```

### Q24. How does `@Transactional` work? Explain propagation and rollback rules.

Spring wraps the bean in an **AOP proxy**. When a `@Transactional` method is called **through the proxy**, Spring starts a transaction, runs the method, and then **commits** if the method returns normally or **rolls back** if it throws a qualifying exception.

**Rollback rules:**
- **Default:** roll back on unchecked exceptions (`RuntimeException`) and `Error`.
- **Checked exceptions do NOT roll back by default.** Use `@Transactional(rollbackFor = Exception.class)` if they should.

**Propagation** controls what happens when a transaction already exists:

| Propagation | Behaviour |
|---|---|
| `REQUIRED` (default) | Join the existing transaction, or create one |
| `REQUIRES_NEW` | Suspend the existing one and always start a new one (e.g. an audit log that must persist even if the outer transaction rolls back) |
| `SUPPORTS` | Join if one exists, otherwise run without a transaction |
| `MANDATORY` | Must run inside an existing transaction, otherwise throw |
| `NOT_SUPPORTED` | Suspend any existing transaction and run without one |
| `NEVER` | Throw if a transaction exists |
| `NESTED` | Create a savepoint inside the existing transaction; the inner part can roll back alone |

Other attributes: `isolation` (e.g. `READ_COMMITTED`), `timeout`, and `readOnly = true` (an optimisation hint for query-only methods).

Put `@Transactional` on the **service layer**. That's where a business operation spanning several repository calls lives.

### Q25. Why does `@Transactional` sometimes not work?

1. **Self-invocation:** calling `this.saveOrder()` from another method in the same class skips the proxy, so no transaction starts. Fix it by moving the method to another bean, or by using `TransactionTemplate`.
2. **Private (or final) methods:** the proxy can't intercept them.
3. **A checked exception is thrown:** no rollback by default (Q24).
4. **The exception is swallowed:** if you `catch` it inside the method, Spring never sees it and commits.
5. **The object isn't a Spring bean:** if you created it with `new`, there's no proxy.
6. **Work runs on another thread:** transactions are bound to the current thread, so `@Async` or manually started threads run outside it.

### Q26. What is the N+1 select problem, and how do you fix it?

You load N parent rows with **1** query, then touch a lazy association on each one, which fires **N** more queries.

```java
List<Department> depts = deptRepo.findAll();     // 1 query
depts.forEach(d -> d.getStudents().size());       // +1 query per department → N+1
```

**Fixes:**
- **`JOIN FETCH`** in JPQL: `SELECT d FROM Department d JOIN FETCH d.students`
- **`@EntityGraph(attributePaths = "students")`** on the repository method
- **Batch fetching:** `spring.jpa.properties.hibernate.default_batch_fetch_size=50` (or `@BatchSize`) loads lazy collections in groups using `IN (...)`
- **DTO projections:** select only the columns you need

**Default fetch types:** `@OneToMany` and `@ManyToMany` are **LAZY**; `@ManyToOne` and `@OneToOne` are **EAGER**. A common best practice is to make every association LAZY and fetch explicitly per use case.

Watch out: using `JOIN FETCH` on a collection together with pagination makes Hibernate paginate in memory. To spot N+1 problems, turn on `spring.jpa.show-sql=true` or Hibernate statistics.

### Q27. How do you implement pagination and sorting?

Accept a `Pageable` and return a page:

```java
@GetMapping("/students")              // ?page=0&size=10&sort=name,asc
public PagedModel<StudentResponse> list(Pageable pageable) {
    return new PagedModel<>(repo.findAll(pageable).map(StudentResponse::from));
}

// Building one in code
Pageable p = PageRequest.of(0, 10, Sort.by("name").ascending());
Page<Student> page = repo.findByCity("Pune", p);
```

- Page numbers are **0-based**.
- **`Page<T>`** gives the content plus `totalElements` and `totalPages`. It runs an extra **count query**.
- **`Slice<T>`** gives the content plus `hasNext()` only, with no count query. It's cheaper, e.g. for infinite scroll.
- Wrap the page in `PagedModel` (or your own DTO) before returning it. That gives clients a stable JSON shape, and recent Spring Data versions warn if you serialise `PageImpl` directly.

---

## 4. Security and Testing

### Q28. How does Spring Security work?

Spring Security is a **chain of servlet filters** that run before your controller:

```
Request → DelegatingFilterProxy → FilterChainProxy → SecurityFilterChain
   [ CORS → CSRF → authentication filter(s) → ExceptionTranslationFilter → AuthorizationFilter ]
→ DispatcherServlet → Controller
```

- **Authentication (who are you?):** an authentication filter extracts the credentials and passes them to the `AuthenticationManager`, which delegates to an `AuthenticationProvider`. The provider loads the user with a `UserDetailsService` and checks the password with a `PasswordEncoder` (BCrypt). The result is stored in the `SecurityContextHolder`.
- **Authorization (what can you do?):** URL rules in the filter chain, plus method-level checks like `@PreAuthorize("hasRole('ADMIN')")` (turn these on with `@EnableMethodSecurity`).
- **Starter defaults:** just adding the starter secures **every** endpoint, with a default user `user` and a generated password printed in the logs.

Modern configuration uses a `SecurityFilterChain` bean (`WebSecurityConfigurerAdapter` was removed in Spring Security 6):

```java
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())   // acceptable for stateless token-based APIs
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/auth/**", "/actuator/health").permitAll()
                .requestMatchers(HttpMethod.DELETE, "/students/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }

    @Bean
    PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(); }
}
```

### Q29. Explain JWT-based authentication.

A **JWT** has the form `header.payload.signature`, each part Base64URL-encoded. The payload carries **claims** such as `sub`, `roles`, and `exp`. The token is **signed** (so it can't be tampered with) but **not encrypted**, which means anyone can read it. Never put secrets in it.

**Flow:**
1. The client sends credentials to `POST /auth/login`.
2. The server authenticates them and returns a signed JWT with a short expiry (e.g. 15 min), and often a refresh token too.
3. The client sends `Authorization: Bearer <token>` on every request.
4. A filter verifies the signature and expiry, builds an `Authentication`, and puts it in the `SecurityContext`. No server session is needed, so this is **stateless**.

- **Pros:** stateless, scales horizontally, and any service with the key can verify the token. That makes it a good fit for microservices.
- **Cons:** you can't easily revoke a token before it expires. Mitigate this with short-lived access tokens, refresh tokens, and a deny-list for logout if needed.

In production, prefer standard **OAuth2 / OpenID Connect**. An authorization server (Keycloak, Okta, Auth0, Spring Authorization Server) issues the tokens, and your services validate them as **resource servers** (`spring-boot-starter-oauth2-resource-server`). See Q48.

### Q30. How do you test a Spring Boot application?

| Annotation / tool | What it loads | Use it for |
|---|---|---|
| Plain JUnit + Mockito (`@Mock`, `@InjectMocks`) | No Spring at all | Fast unit tests of services |
| `@WebMvcTest(StudentController.class)` | Web layer only (controllers, advice, filters) + `MockMvc` | Controller tests, with services mocked |
| `@DataJpaTest` | JPA repositories + embedded DB; each test rolls back | Repository and query tests |
| `@SpringBootTest` | The full application context | Integration tests (`webEnvironment = RANDOM_PORT` for real HTTP) |
| `@MockitoBean` | — | Replaces a bean in the context with a Mockito mock (successor to `@MockBean`, which is deprecated since Boot 3.4) |
| Testcontainers | A real DB or Kafka in Docker | Realistic integration tests |

```java
@WebMvcTest(StudentController.class)
class StudentControllerTest {

    @Autowired MockMvc mvc;
    @MockitoBean StudentService service;

    @Test
    void returns404WhenStudentMissing() throws Exception {
        when(service.findById(99L)).thenThrow(new ResourceNotFoundException("Student 99 not found"));

        mvc.perform(get("/students/99"))
           .andExpect(status().isNotFound());
    }
}
```

---

## 5. Microservices Concepts

### Q31. What are microservices? How do they differ from a monolith?

**Microservices** is an architectural style in which an application is built as a set of **small, independently deployable services**. Each service owns **one business capability and its own data**, and services talk over the network (HTTP/REST, gRPC, messaging).

| | Monolith | Microservices |
|---|---|---|
| Deployment | One unit; any change redeploys everything | Each service is deployed independently |
| Scaling | Scale the whole app | Scale only the busy services |
| Data | One shared database | Database per service |
| Failure | One bug can take everything down | Failures can be isolated |
| Tech stack | One stack | Can differ per service |
| Teams | One shared codebase | A team owns a service end-to-end |
| Complexity | Simple to build, test, and debug | Distributed-system complexity |

### Q32. What are the advantages and challenges of microservices?

**Advantages:** independent deployment and faster releases, independent scaling, fault isolation, team autonomy, freedom to pick the right tech per service, and smaller codebases that are easier to understand.

**Challenges:**
- The network is unreliable: latency, timeouts, and partial failures
- Keeping data consistent without ACID transactions across services
- Debugging a request that crosses many services (you need tracing)
- Operational overhead: many deployables, pipelines, configs, and dashboards
- End-to-end testing and API versioning
- Securing service-to-service calls

**When NOT to use them:** a small team, an early-stage product, or unclear domain boundaries. The usual advice is to start with a well-structured **modular monolith** and extract services only when there's a real need.

### Q33. How do you decide service boundaries or break up a monolith?

- **By business capability:** Order, Payment, Inventory, Shipping, Notification.
- **By DDD bounded context:** each service owns one consistent model and vocabulary. A "Product" in Catalog is not the same thing as a "Product" in Shipping.
- **High cohesion, loose coupling:** things that change together stay together.
- **Each service owns its data.** Split along business lines, **not technical layers** (no "DAO service").

**To migrate,** use the **Strangler Fig pattern**: put a gateway or facade in front of the monolith, move one feature at a time into a new service, route that feature's traffic to it, and retire the old code. Repeat.

**Anti-pattern: the distributed monolith.** Services that must be deployed together, share a database, or depend on long chains of synchronous calls give you all the costs of microservices and none of the benefits.

### Q34. What is the database-per-service pattern? How do you query data that spans services?

Each service keeps its tables or database **private**. Other services get at that data only through its API or its events, never by querying its database directly.

**Why:** loose coupling, independent schema changes, the freedom to pick the best store per service (*polyglot persistence*: PostgreSQL for orders, Redis for carts, Elasticsearch for search), and independent scaling.

**Querying across services** (there are no SQL joins between services):
- **API Composition:** an aggregator (or the gateway/BFF) calls several services and merges the results.
- **CQRS (Command Query Responsibility Segregation):** keep the write model separate from the read model. Services publish events, and a read-side service builds a denormalised, query-friendly view from them.
- **Replicate data via events:** a service keeps a local read-only copy of the data it needs (e.g. Order keeps the customer's name).

For writes that span services, use a **Saga** (Q45).

### Q35. Synchronous vs asynchronous communication: when do you use each?

| | Synchronous (REST, gRPC) | Asynchronous (Kafka, RabbitMQ) |
|---|---|---|
| Model | Send a request, wait for the response | Publish a message/event and carry on |
| Coupling | The callee must be up right now (temporal coupling) | Producer and consumer are decoupled in time |
| When things fail | A slow or down callee slows the caller, which can cascade | The broker buffers messages and the consumer catches up later |
| Consistency | Immediate | Eventual |
| Complexity | Simple and easy to debug | Broker infrastructure, duplicates, ordering, harder tracing |

**Rule of thumb:** go synchronous when the caller needs an answer *now* (check stock before showing checkout). Go asynchronous for side effects and for letting other services know something happened (`OrderPlaced` → email, analytics, shipping).

### Q36. `RestTemplate` vs `RestClient` vs `WebClient` vs OpenFeign?

| Client | Style | Notes |
|---|---|---|
| `RestTemplate` | Synchronous, template-based | Legacy. Spring has [announced its deprecation](https://spring.io/blog/2025/09/30/the-state-of-http-clients-in-spring): formally deprecated in Framework 7.1, removal planned for 8.0 |
| `RestClient` | Synchronous, fluent (Spring 6.1+) | Recommended for regular (blocking) apps |
| `WebClient` | Reactive, non-blocking (WebFlux) | High concurrency, streaming, reactive stacks |
| OpenFeign | Declarative interface | Spring Cloud; works with discovery and load balancing |
| HTTP Interfaces (`@HttpExchange`) | Declarative interface built into Spring 6+ | Spring's own alternative to Feign |

```java
// RestClient (built from a @LoadBalanced builder, see Q40)
StudentDto s = restClient.get()
        .uri("http://STUDENT-MS/students/{id}", id)
        .retrieve()
        .body(StudentDto.class);

// OpenFeign (add @EnableFeignClients on the main class)
@FeignClient(name = "STUDENT-MS")
public interface StudentClient {
    @GetMapping("/students/{id}")
    StudentDto getStudent(@PathVariable Long id);
}
```

### Q37. What are eventual consistency and idempotency, and why do they matter?

- **Eventual consistency:** right after a change, services may briefly see different data, but they catch up once all events are processed. It's the trade-off you accept for availability and loose coupling. (The CAP theorem says that during a network partition you must choose between consistency and availability.)
- **Idempotency:** handling the same request or message twice has the same effect as handling it once. This is essential, because retries and *at-least-once* delivery **will** produce duplicates.

**Techniques:**
- **Idempotency key:** the client sends a unique `Idempotency-Key` header. The server stores the keys it has processed and returns the saved result for repeats. This is the classic approach for payments.
- **Idempotent consumer:** record the IDs of messages you've processed and skip any you've already seen.
- **Natural safeguards:** unique constraints, upserts, and state checks (if the order is already `PAID`, ignore the duplicate).

### Q38. How does event-driven communication work with Kafka?

Producers publish events to a **topic**, and any number of services can subscribe. The producer doesn't know who the consumers are.

**Kafka essentials:**
- A **topic** is split into **partitions**: ordered, append-only logs in which every message has an **offset**.
- Messages with the same **key** go to the same partition, so ordering is guaranteed **per key** (e.g. per order ID).
- **Consumer group:** within a group, each partition is read by one consumer, which gives you parallelism. Each separate group receives every message.
- Messages are **retained** for a set time or size, so consumers can **replay** them.

**Kafka vs RabbitMQ:** Kafka is a distributed, durable log built for high-throughput event streaming and replay. RabbitMQ is a traditional message broker with flexible routing (exchanges and queues), and messages are usually removed once acknowledged.

```java
// Producer
kafkaTemplate.send("order-events", orderId.toString(), new OrderPlaced(orderId));

// Consumer
@KafkaListener(topics = "order-events", groupId = "notification-service")
public void onOrderPlaced(OrderPlaced event) {
    emailService.sendConfirmation(event.orderId());
}
```

**The dual-write problem and the Transactional Outbox:** saving to the DB and publishing to Kafka are writes to two different systems, so one can succeed while the other fails. The fix is to write the business change *and* an event row to an `outbox` table **in the same DB transaction**. A separate relay (a poller, or CDC with Debezium) then publishes the outbox rows to Kafka.

---

## 6. Spring Cloud Building Blocks

### Q39. What is service discovery? How does Eureka work?

In the cloud, instances start, stop, and scale all the time, and their IPs and ports change, so hard-coded URLs break. A **service registry** keeps an up-to-date list of the live instances.

**Eureka** (Spring Cloud Netflix):
1. **Eureka Server** is the registry (`@EnableEurekaServer`, port 8761 by convention).
2. **Clients register** on startup under their `spring.application.name` (e.g. `STUDENT-MS`).
3. Clients send **heartbeats** (every 30 s by default). An instance that stops sending them is evicted (after about 90 s).
4. Clients **fetch and cache** the registry, so calls keep working even if Eureka is briefly down.
5. **Self-preservation mode:** if many heartbeats are lost at once (probably a network problem), Eureka stops evicting instances instead of emptying the registry.

```properties
# eureka-server
server.port=8761
eureka.client.register-with-eureka=false
eureka.client.fetch-registry=false

# each microservice
spring.application.name=STUDENT-MS
eureka.client.service-url.defaultZone=http://localhost:8761/eureka
```

There are two discovery styles:
- **Client-side discovery** (Eureka): the client looks up the instances and picks one.
- **Server-side discovery:** the client calls a router or load balancer that does the lookup (e.g. Kubernetes Services, AWS ALB).

On **Kubernetes**, its built-in DNS-based discovery often replaces Eureka.

### Q40. What is client-side load balancing in Spring Cloud?

The calling service gets the list of instances for a service name (from Eureka) and picks one itself, **round-robin** by default (random is also available). **Spring Cloud LoadBalancer** does this job; it replaced Netflix Ribbon.

```java
@Configuration
class HttpConfig {
    @Bean
    @LoadBalanced                          // resolve service names through the registry
    RestClient.Builder restClientBuilder() {
        return RestClient.builder();
    }
}

// Usage: the "host" is the service name, not a real host
restClientBuilder.build()
        .get().uri("http://STUDENT-MS/students/1")
        .retrieve().body(StudentDto.class);
```

It also works with `RestTemplate`, `WebClient.Builder`, OpenFeign, and `lb://` URIs in Spring Cloud Gateway.

The alternative is **server-side** load balancing (NGINX, AWS ALB, a Kubernetes Service): the client calls a single address and the load balancer spreads the traffic.

### Q41. What is an API Gateway? How does Spring Cloud Gateway work?

An API gateway is the **single entry point** between clients and your microservices. Clients call one host, and the gateway routes each request to the right service.

It's the one place to handle cross-cutting concerns: routing, authentication (validating JWTs), rate limiting, CORS, SSL termination, header rewriting, retries and circuit breaking, logging and tracing, and response aggregation.

**Spring Cloud Gateway** replaced Netflix Zuul. Each **route** is made of:
- an **ID**
- a destination **URI**
- **predicates** that decide when the route matches: `Path`, `Method`, `Header`, `Host`
- **filters** that modify the request or response: `StripPrefix`, `AddRequestHeader`, `RequestRateLimiter`, `CircuitBreaker`, `Retry`

```yaml
spring:
  cloud:
    gateway:
      server:
        webflux:                     # Spring Cloud 2025.0+; older versions use spring.cloud.gateway.routes
          routes:
            - id: student-route
              uri: lb://STUDENT-MS   # lb:// = load-balance across instances registered in Eureka
              predicates:
                - Path=/students-api/**
              filters:
                - StripPrefix=1      # /students-api/students → /students
```

- The default flavour runs on **Spring WebFlux/Netty** (reactive), so don't add `spring-boot-starter-web` to it. There's also a Spring MVC-based variant. Since Spring Cloud 2025.0 the starters are named `spring-cloud-starter-gateway-server-webflux` and `spring-cloud-starter-gateway-server-webmvc` ([release announcement](https://spring.io/blog/2025/05/29/spring-cloud-2025-0-0-is-abvailable/)).
- **BFF (Backend for Frontend):** a separate gateway per client type (web, mobile), each tailored to that client.

### Q42. How do you manage configuration centrally? (Spring Cloud Config)

With many services and several environments, config scattered across jars quickly becomes unmanageable. A **Spring Cloud Config Server** serves the config for every service from one place, usually a **Git repo**, which makes it versioned and auditable.

- **Repo files** are named `{application}-{profile}.yml`, e.g. `student-ms-prod.yml`.
- **Server:** `@EnableConfigServer` + `spring.cloud.config.server.git.uri=https://github.com/<org>/config-repo`
- **Client:** `spring.config.import=optional:configserver:http://localhost:8888`

**To refresh without a restart:**
- Annotate beans with `@RefreshScope`, then call `POST /actuator/refresh` on the instance.
- **Spring Cloud Bus** (over Kafka or RabbitMQ) broadcasts the refresh to every instance through `/actuator/busrefresh`.

**Secrets:** never store them in plain text. Use Config Server encryption (`{cipher}...`) or a secrets manager (HashiCorp Vault, AWS Secrets Manager). On Kubernetes, ConfigMaps and Secrets are a common alternative.

### Q43. What is the Circuit Breaker pattern? Explain its states.

A circuit breaker **stops calling a dependency that keeps failing**. That way threads aren't stuck waiting and the failure doesn't cascade. While open, it fails fast and returns a fallback, and every so often it checks whether the dependency has recovered.

```
CLOSED    --(failure rate ≥ threshold)--> OPEN
OPEN      --(wait duration elapsed)-----> HALF_OPEN
HALF_OPEN --(trial calls succeed)-------> CLOSED
HALF_OPEN --(trial calls fail)----------> OPEN
```

- **CLOSED:** calls go through normally, and their results are recorded in a sliding window.
- **OPEN:** the failure (or slow-call) rate crossed the threshold. Calls are rejected immediately and the fallback is used, for a set wait period.
- **HALF_OPEN:** a few trial calls are let through. If they succeed it goes back to CLOSED; if they fail it goes back to OPEN.

Use **Resilience4j**. Netflix Hystrix is in maintenance mode and not used for new projects.

```java
@CircuitBreaker(name = "inventory", fallbackMethod = "stockFallback")
public StockDto checkStock(Long productId) {
    return inventoryClient.getStock(productId);
}

public StockDto stockFallback(Long productId, Throwable ex) {   // same params + Throwable
    return StockDto.unknown(productId);                          // degrade gracefully
}
```

```yaml
resilience4j:
  circuitbreaker:
    instances:
      inventory:
        sliding-window-size: 10
        failure-rate-threshold: 50
        wait-duration-in-open-state: 10s
        permitted-number-of-calls-in-half-open-state: 3
```

Dependency: `spring-cloud-starter-circuitbreaker-resilience4j` (or the Resilience4j Spring Boot starter), plus AOP support so the annotations work.

### Q44. What other resilience patterns should you know?

| Pattern | Problem it solves | Tip |
|---|---|---|
| **Timeout** | Waiting forever on a slow service | Always set connect/read timeouts; Resilience4j `TimeLimiter` |
| **Retry** | Transient failures (a network blip) | Exponential backoff + jitter; cap the attempts; only retry idempotent operations |
| **Circuit breaker** | Repeatedly calling a failing service | See Q43 |
| **Bulkhead** | One slow dependency using up all the threads | Limit concurrent calls per dependency (semaphore or thread pool) |
| **Rate limiter** | Overload or abuse | Limit calls per time period, at the gateway (`RequestRateLimiter` + Redis) or inside the service |
| **Fallback** | Still needing a response when a dependency fails | Cached or default data, or a degraded feature |

- **Resilience4j's default decorator order** is `Retry( CircuitBreaker( RateLimiter( TimeLimiter( Bulkhead( call ) ) ) ) )`, so retry is the outermost layer.
- **Beware retry storms:** retries at every layer multiply the load on a service that is already struggling.

---

## 7. Consistency, Observability and Deployment

### Q45. How do you handle transactions across microservices? Explain the Saga pattern.

There's no single ACID transaction across several services' databases. Two-phase commit (2PC/XA) exists, but teams avoid it for four reasons:
- it blocks while waiting
- the coordinator becomes a bottleneck and a single point of failure
- it hurts availability
- many modern databases and brokers don't support it

A **Saga** is a **sequence of local transactions**, one per service. Each step commits locally and triggers the next one. If a step fails, the steps already completed are undone by **compensating transactions**.

**Example: placing an order**

| Step | Service | Action | Compensation |
|---|---|---|---|
| 1 | Order | Create order as `PENDING` | Mark order `CANCELLED` |
| 2 | Payment | Charge the customer | Refund |
| 3 | Inventory | Reserve stock | Release stock |
| 4 | Order | Mark order `CONFIRMED` | — |

If step 3 fails (out of stock), the saga refunds the payment and then cancels the order.

There are two ways to coordinate a saga:
- **Choreography:** there's no coordinator. Each service listens for events and reacts (`OrderCreated` → Payment charges → `PaymentCompleted` → Inventory reserves → …). It's simple for a few steps, but the flow is implicit and gets hard to follow as it grows.
- **Orchestration:** a central orchestrator (e.g. `OrderSaga`) tells each service what to do and handles failures. The flow is explicit and easy to monitor, at the cost of one more component. Tools include Temporal, Camunda, Axon, and Eventuate Tram.

Sagas aren't isolated: other transactions can see the in-between state. Handle that with *semantic locks*, such as a `PENDING` status. Compensations must also be **idempotent**.

### Q46. What is distributed tracing? How do you implement it in Spring Boot?

One user request may pass through gateway → order → payment → inventory. Tracing stitches those hops together into a single picture.

- **Trace ID:** stays the same for the request's whole journey.
- **Span ID:** one per unit of work or hop. Spans form a tree, each with its own timing.
- Both IDs travel in HTTP and message headers (W3C `traceparent`, or B3).

In Spring Boot 3+, use **Micrometer Tracing**. It replaces Spring Cloud Sleuth, which doesn't support Boot 3. Add an OpenTelemetry (or Brave) bridge and export the spans to **Zipkin**, Jaeger, or Grafana Tempo.

```xml
<!-- Boot 3.x example -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-tracing-bridge-otel</artifactId>
</dependency>
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-exporter-zipkin</artifactId>
</dependency>
```

```properties
# Default is 0.1 (10% of requests); 1.0 traces everything, which suits dev
management.tracing.sampling.probability=1.0
```

Trace and span IDs are added to log lines automatically. That lets you search the logs of every service for one trace ID, which then works as a **correlation ID**.

### Q47. How do you monitor microservices? (logging, metrics, alerting)

Observability rests on three pillars:

| Pillar | Answers | Typical stack |
|---|---|---|
| **Logs** | What happened? | Centralised: ELK/EFK (Elasticsearch, Logstash/Fluentd, Kibana) or Grafana Loki |
| **Metrics** | How is it behaving over time? | Micrometer → Prometheus → Grafana dashboards + alerts |
| **Traces** | Where did the time go across services? | Micrometer Tracing → Zipkin / Jaeger / Tempo |

Good practices:
- **Ship logs to one place.** Containers are short-lived, and their logs disappear with them.
- **Use structured (JSON) logs.** Spring Boot 3.4+ supports this out of the box: `logging.structured.format.console=ecs` (or `logstash`, `gelf`).
- **Include the trace ID** in every log line (Q46).
- **Track RED metrics** per service: **R**ate, **E**rrors, **D**uration (latency percentiles such as p95/p99).
- **Alert on what users feel** (error rate, latency), not just CPU.
- **Use Actuator health groups** for liveness and readiness (Q49).

### Q48. How do you secure microservices?

- **Edge security at the gateway:** use OAuth2 / OpenID Connect. Users log in through an authorization server (Keycloak, Okta, Auth0, Spring Authorization Server) and receive a JWT access token. The gateway validates the token and passes it downstream (`TokenRelay` filter).
- **Every service is a resource server too.** Each one validates the JWT itself and checks scopes and roles. Don't trust a request just because it comes from "inside the network" (zero trust / defence in depth).

  ```properties
  spring.security.oauth2.resourceserver.jwt.issuer-uri=https://auth.example.com/realms/demo
  ```

- **Service-to-service calls:** use the OAuth2 **client credentials** grant (each service gets its own token), and/or **mTLS**, often through a service mesh such as Istio or Linkerd.
- **Secrets:** never in code or Git. Use Vault, a cloud secrets manager, or Kubernetes Secrets.
- **Also:** HTTPS everywhere, rate limiting at the gateway, input validation in every service, least-privilege DB users, and dependency vulnerability scanning.

### Q49. How do you deploy microservices? (Docker, Kubernetes, health probes)

**Containerise** each service:

```dockerfile
FROM eclipse-temurin:21-jre
COPY target/student-ms.jar app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

Or skip the Dockerfile with `./mvnw spring-boot:build-image` (Cloud Native Buildpacks).

**Orchestrate with Kubernetes:**

| Object | Purpose |
|---|---|
| Deployment | Desired replica count, rolling updates, self-healing |
| Service | A stable DNS name + load balancing across pods (built-in discovery) |
| ConfigMap / Secret | Externalised config and credentials |
| HorizontalPodAutoscaler | Scales replicas on CPU or custom metrics |
| Ingress / Gateway API | The external HTTP entry point |

**Health probes:** Actuator provides `/actuator/health/liveness` and `/actuator/health/readiness`. They're turned on automatically when the app runs on Kubernetes; elsewhere, set `management.endpoint.health.probes.enabled=true`.
- **Liveness fails** → Kubernetes **restarts** the container.
- **Readiness fails** → the pod is **taken out of load balancing** until it's ready (e.g. while it's still warming up).

Also plan for:
- **Graceful shutdown** (`server.shutdown=graceful`, the default since Boot 3.4), so in-flight requests finish during a rollout.
- **A deployment strategy:** rolling, blue-green, or canary.
- **A separate CI/CD pipeline** for each service.

### Q50. Design question: "Design an e-commerce order system using microservices."

Use this question to show how all the pieces fit together.

```
                     Web / Mobile clients
                              │
                       ┌──────▼──────┐
                       │ API Gateway │  JWT validation · routing · rate limiting
                       └──────┬──────┘
        ┌──────────────┬──────┴───────┬───────────────┐
        ▼              ▼              ▼               ▼
   User Service  Product Service  Order Service ──► Inventory Service
                                      │         (sync REST + circuit breaker)
                                      │ publishes OrderPlaced
                               ┌──────▼──────┐
                               │    Kafka    │
                               └──┬───────┬──┘
                                  ▼       ▼
                        Payment Service  Notification Service

Platform: Eureka · Config Server · Micrometer Tracing + Zipkin · Prometheus + Grafana · Loki/ELK · Kubernetes
```

**Talking points:**
1. **Boundaries:** split by business capability, with a database per service (Order → PostgreSQL, Product search → Elasticsearch, Cart → Redis).
2. **Entry point:** the gateway handles auth, routing, and rate limiting, and each service also validates the JWT.
3. **Communication:** synchronous where you need an answer now (the stock check), and asynchronous events for side effects (payment, email, shipping).
4. **Consistency:** placing an order is a **saga**: Order `PENDING` → Payment → Inventory → `CONFIRMED`, with compensations on failure. Add the **outbox** for reliable event publishing and **idempotent consumers**.
5. **Resilience:** timeouts, retries with backoff, and a circuit breaker + fallback on the Inventory call.
6. **Discovery and config:** Eureka (or Kubernetes Services) plus the Config Server.
7. **Observability:** end-to-end trace IDs, central logs, RED metrics, and alerts.
8. **Deployment:** one container per service on Kubernetes, with HPA, liveness/readiness probes, and CI/CD per service.
9. **Scaling:** scale the read-heavy Product service (add a cache) separately from Order.
