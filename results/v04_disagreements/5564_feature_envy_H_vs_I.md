# Smell occurrence 5564 — feature envy / major

- **Code under review:** `org.apache.cxf.rs.security.jose.jwk.JwkUtils.fromRSAPrivateKey RSAPrivateKey|String|String`
- **Lines:** 448–469
- **Human label:** `H`
- **v04 label:** `I`

## Original LLM review (under test)

```
**Summary**

`JwkUtils` is a utility class providing a comprehensive set of static methods for working with JSON Web Keys (JWK) and JWK Sets. Its responsibilities include serialization/deserialization, encoding/decoding, encryption/decryption, signing/verifying, conversion between JWKs and Java key/certificate types, and loading keys from various sources (streams, properties, messages). The methods are highly cohesive around JWK manipulation, but the class is large and covers a wide range of concerns, from low-level encoding to integration with CXF/Jose APIs.

**Review Comments**

---

**1. Overly Long Methods with Multiple Responsibilities**

Several methods in `JwkUtils` are quite lengthy and perform multiple distinct operations, making them harder to understand, maintain, and test. For example:

```java
public static JsonWebKeys loadJwkSet(Properties props, Bus bus, JweDecryptionProvider jwe) {
    String keyContent = null;
    String keyStoreLoc = props.getProperty(JoseConstants.RSSEC_KEY_STORE_FILE);
    if (keyStoreLoc != null) {
        try {
            InputStream is = JoseUtils.getResourceStream(keyStoreLoc, bus);
            if (is == null) {
                throw new JwkException("Error in loading keystore location: " + keyStoreLoc);
            }
            try (InputStream isResource = is) {
                keyContent = IOUtils.readStringFromStream(isResource);
            }
        } catch (Exception ex) {
            throw new JwkException(ex);
        }
    } else {
        keyContent = props.getProperty(JoseConstants.RSSEC_KEY_STORE_JWKSET);
        if (keyContent == null) {
            keyContent = props.getProperty(JoseConstants.RSSEC_KEY_STORE_JWKKEY);
        }
    }
    if (jwe != null) {
        keyContent = jwe.decrypt(keyContent).getContentText();
    }
    JwkReaderWriter reader = new JwkReaderWriter();
    if (props.getProperty(JoseConstants.RSSEC_KEY_STORE_JWKKEY) == null) {
        return reader.jsonToJwkSet(keyContent);
    }
    JsonWebKey jwk = reader.jsonToJwk(keyContent);
    return new JsonWebKeys(jwk);
}
```

This method is responsible for:
- Locating the key material (from file or properties)
- Reading the content (with error handling)
- Optionally decrypting the content
- Deciding whether to parse as a set or a single key
- Returning the parsed result

Each of these could be extracted into smaller, intention-revealing helper methods (e.g., `readKeyContent`, `decryptKeyContent`, `parseJwkOrJwkSet`). This would improve readability and make the method easier to reason about and test in isolation. See [Fowler's Extract Method](https://refactoring.com/catalog/extractMethod.html).

---

**2. Utility Class with Feature Envy Toward JsonWebKey**

Many methods in `JwkUtils` operate by extracting properties from `JsonWebKey` instances, manipulating them, and then returning new keys or Java key objects. For example:

```java
public static RSAPublicKey toRSAPublicKey(JsonWebKey jwk, boolean checkX509) {
    String encodedModulus = (String)jwk.getProperty(JsonWebKey.RSA_MODULUS);
    String encodedPublicExponent = (String)jwk.getProperty(JsonWebKey.RSA_PUBLIC_EXP);
    if (encodedModulus != null) {
        return CryptoUtils.getRSAPublicKey(encodedModulus, encodedPublicExponent);
    } else if (checkX509) {
        List<X509Certificate> chain = toX509CertificateChain(jwk);
        return (RSAPublicKey)chain.get(0).getPublicKey();
    }
    return null;
}
```

and

```java
public static JsonWebKey fromRSAPublicKey(RSAPublicKey pk, String algo, String kid) {
    JsonWebKey jwk = prepareRSAJwk(pk.getModulus(), algo, kid);
    String encodedPublicExponent = Base64UrlUtility.encode(pk.getPublicExponent().toByteArray());
    jwk.setProperty(JsonWebKey.RSA_PUBLIC_EXP, encodedPublicExponent);
    return jwk;
}
```

These methods are deeply concerned with the internal structure of `JsonWebKey`, often setting or getting multiple properties. This suggests that some of this logic might be more appropriately placed within the `JsonWebKey` class itself, as instance or static factory methods. This would encapsulate the knowledge of how to construct or extract key material, reducing coupling and making the codebase easier to evolve. See [Fowler's Move Method](https://refactoring.com/catalog/moveMethod.html).

---

**3. Data Class Usage and Lack of Encapsulation**

The `JsonWebKey` class (as used here) appears to be a data holder with little behavior of its own, manipulated in detail by `JwkUtils`. For example, methods like `fromRSAPrivateKey`, `fromECPublicKey`, and `fromSecretKey` all construct a `JsonWebKey` and set its properties externally. Similarly, conversion methods extract properties directly.

This pattern leads to a proliferation of code that knows about the internal structure of `JsonWebKey`, making it harder to change or extend the key representation. It would be preferable for `JsonWebKey` to provide richer construction and conversion methods, encapsulating its own invariants and reducing the need for external manipulation. This would also help prevent errors where required properties are omitted or set inconsistently.

---

**4. Large Utility Class with Mixed Abstraction Levels**

`JwkUtils` contains a very large number of static methods, ranging from low-level encoding/decoding to high-level integration with CXF `Message` and `Properties`. This makes the class difficult to navigate and increases the risk of accidental coupling between unrelated concerns.

For example, methods like `getThumbprint`, `fromRSAPublicKey`, and `toSecretKey` are low-level, while `loadJwkSet` and `loadJsonWebKey` are high-level, dealing with application context and configuration. Splitting the class into smaller, more focused utility classes (e.g., `JwkSerializationUtils`, `JwkConversionUtils`, `JwkLoadingUtils`) would improve cohesion and maintainability.

---

**5. Repeated Patterns and Opportunities for Further Extraction**

There are several repeated patterns, such as reading from an `InputStream` or `String`, encoding/decoding, and wrapping/unwrapping keys. For example, the various `readJwkKey` and `readJwkSet` overloads could be unified or refactored to reduce duplication. Similarly, the encryption/decryption and signing/verification methods follow similar patterns that could be abstracted.

---

**Summary**

While `JwkUtils` is cohesive in its focus on JWK manipulation, it suffers from long, multi-responsibility methods, a tendency to manipulate data classes externally, and a large, monolithic structure that mixes abstraction levels. Refactoring to extract smaller methods, move behavior closer to the data it operates on, and split the utility class by concern would improve readability, maintainability, and encapsulation.
```

## v04 judge reasoning (REASONING + CLASSIFICATION + JUSTIFICATION)

```
REASONING:
  Step 1 (TYPE): mentions "Feature Envy" explicitly in section 2 ("Utility Class with Feature Envy Toward JsonWebKey")
  Step 2 (LOCATION): associates Feature Envy with methods such as `fromRSAPublicKey`, `toRSAPublicKey`, and by extension, methods like `fromRSAPrivateKey` (the targeted snippet), as it discusses methods that manipulate `JsonWebKey` properties directly
  Step 3 (DESCRIPTION): explains that these methods "operate by extracting properties from `JsonWebKey` instances, manipulating them, and then returning new keys or Java key objects," and that this logic "might be more appropriately placed within the `JsonWebKey` class itself"
  Step 4 (REFACTORING): suggests "move behavior closer to the data it operates on" and references Fowler's Move Method

CLASSIFICATION: I

JUSTIFICATION: All four criteria are satisfied—Feature Envy is named, associated with the targeted snippet, described accurately, and a Fowler-compatible refactoring (Move Method) is suggested.
```