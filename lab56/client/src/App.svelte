<script>
  import axios from 'axios';
  let authorized = false;
  let register = { email: '', password: '' };
  let login = { email: 'kefirchik3@gmail.com', password: '' };

  function onSubmitLogin() {
    axios.post('/login', login)
      .then(() => authorized = true)
  }
  function onSubmitRegister() {
    axios.post('/register', register)
      .then(() => alert('Registered successfully'))
  }
</script>

<main>
  {#if !authorized}
    <form on:submit|preventDefault={onSubmitLogin}>
      <fieldset>
        <legend>Login</legend>
        <input placeholder="email" type="email" bind:value={login.email} />
        <input
          placeholder="password"
          type="password"
          bind:value={login.password}
        />
        <button type="submit">Login</button>
      </fieldset>
    </form>
  {/if}
  <form on:submit|preventDefault={onSubmitRegister}>
    <fieldset>
      <legend>Register</legend>
      <input placeholder="email" type="email" bind:value={register.email} />
      <input
        placeholder="password"
        type="password"
        bind:value={register.password}
      />
      <button type="submit">Register</button>
    </fieldset>
  </form>
</main>

