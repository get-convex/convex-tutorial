import React, { useState, useEffect } from 'react';
import './Login.css';
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Row, Col, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Login = () => {
    return (
        <Container>
            <h1 className='title'>nearbuy</h1>
            <div style={{ marginLeft: "7rem", marginRight: "7rem" }}>
                <Card className="login_form">
                    <Form>
                        <Form.Group style={{ marginRight: "1rem" }} className="mb-3 center" controlId="formBasicEmail">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control type="email" placeholder="Enter email" />
                            <Form.Text className="text-muted">
                                We'll never share your email with anyone else.
                            </Form.Text>
                        </Form.Group>

                        <Form.Group className="mb-3" style={{ marginRight: "1rem" }} controlId="formBasicPassword">
                            <Form.Label>Password</Form.Label>
                            <Form.Control type="password" placeholder="Password" />
                        </Form.Group>
                    </Form>
                    <Link style={{ display: "inline", paddingTop: "0.5rem", paddingBottom: "0.5rem", textAlign: "center" }} className="button" to="map">submit</Link>
                </Card>
            </div>


        </Container>
    );
};

export default Login;